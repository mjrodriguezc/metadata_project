import pandas as pd
import json
import os
from collections import Counter
import numpy as np
import scispacy
import spacy
import re
import ast
import requests
from os import listdir
from os.path import isfile, join
from functools import reduce
import time
import contextlib
import sys


### NLP task packages
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


### Models implementation packages
from transformers import pipeline
import torch

from transformers import AutoModelForQuestionAnswering, AutoTokenizer


# **************************************** PRE PROCESSING  **********************************************************

@contextlib.contextmanager
def capture_stdout(dest):
    old_stdout = sys.stdout
    try:
        sys.stdout = dest
        yield
    finally:
        sys.stdout = old_stdout

### FUNCTIONS   
def load_data(csv_file):
    try:
        df = pd.read_csv(csv_file)
        return df
    except FileNotFoundError:
        print(f"File not found: {csv_file}")
        return None
    except pd.errors.EmptyDataError:
        print(f"File is empty: {csv_file}")
        return None
    except pd.errors.ParserError as e:
        print(f"Error parsing file: {csv_file}\n{e}")
        return None
    
def combined_text_in_file (df,list_variables, new_name_column):

    df[new_name_column] = (
        df[list_variables]
        .fillna("")
        .agg(" ".join, axis=1)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    return df


#### Cleaning

def remove_stop_words(text):
    tokens = word_tokenize(text)  ### The text is tokenize in here
    stop_words = set(stopwords.words("english"))
    filtered = [w for w in tokens if w.lower() not in stop_words and w.isalpha()]

    return filtered

def remove_special_characters(text):
    """
    This function removes special characters from the text.
    :param text: text
    :return: text without special characters
    """
    if not isinstance(text, str):
        cleaned_string = ""   # or return None if you prefer

    else:
    
        cleaned_string = re.sub(r'[?|$|.|!|@|#|%|^|&|*|(|)|-|_|+|=|;|:|,|<|>|/|{|}|[|]|~|`|\'|\"|\\]',r'', text)

    return cleaned_string

# **************************************** PIPELINE **********************************************************

##### Species extraction

def extract_species_from_existing_text(text):
    nlp = spacy.load("en_ner_bionlp13cg_md") 
    doc= nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]

    dictionary_entities = {}
    for k,v in entities:
        if v not in dictionary_entities:
            dictionary_entities[v]=[]
        dictionary_entities[v].append(k)
    
    return dictionary_entities

def extract_entities(doc):
    out = {}
    for ent in doc.ents:
        out.setdefault(ent.label_, []).append(ent.text)
    return out

### STEP 1. SciSpacy

def run_scispacy_check(df):
    df['Species_Scientific_Name_SciSpacy'] = 'Not found'

    start_time = time.time()

        
    for i, item in df.iterrows():
        list_species_spacy = item['Species_SpaCy']
        list_species_scientific_name = []
       
        if not isinstance(list_species_spacy, list) or not list_species_spacy:
            continue

        for x in list_species_spacy:
            values = x.split(' ')
                #print(values)
            for unique_value in values:
                    #print(unique_value)
                    
                url = f'https://www.ebi.ac.uk/ena/taxonomy/rest/any-name/{unique_value}'
                    #print(url)

                response = requests.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                        #print(data)
                    if data:
                        scientific_name = data[0]['scientificName']
                        tax_id = data[0]['taxId']

                        list_species_scientific_name.append(scientific_name)
                        print(f"Scientific name for {x}: {scientific_name}")

                        ols_url = f"https://www.ebi.ac.uk/ols4/api/search?q={scientific_name}&ontology=ncbitaxon&exact=true"
                        ols_response = requests.get(ols_url).json()

                        if ols_response['response']['numFound'] > 0:
                            term_uri = ols_response['response']['docs'][0]['obo_id']
                            print(f"Connected TaxID {tax_id} to OLS term: {term_uri}")

                            tax_scispacy = term_uri
                        else:
                            tax_scispacy = "No OLS term identified"

                        df.at[i, 'Species_Scientific_Name_TaxID'] = tax_scispacy
                    else:
                        scientific_name = 'Not found'
                        print(f"Scientific name for {x}: {scientific_name}")

        
        df.at[i, 'Species_Scientific_Name_SciSpacy'] = str(list_species_scientific_name)

        

    end_time = time.time()
    print(f"Execution time SciSpacy: {end_time - start_time:.2f} seconds")

    return df


### 2. STEP 2: BioBERT

def run_biobert(df, previous_step_check, column_to_evaluate):

    # Load the BioBERT model and create a pipeline for question answering
    df['Species_BioBERT'] = df.get('Species_BioBERT', 'Not found')
    start_time = time.time()

    model_name = "dmis-lab/biobert-large-cased-v1.1-squad"

    # Load model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForQuestionAnswering.from_pretrained(model_name).to("cuda")

    def answer_question(question, context):
        inputs = tokenizer(
            question,
            context,
            return_tensors="pt",
            truncation=True,
            max_length=256
        ).to("cuda")

        with torch.no_grad():
            outputs = model(**inputs)

        # Get answer span positions
        start = torch.argmax(outputs.start_logits)
        end   = torch.argmax(outputs.end_logits) + 1

        # Decode the answer
        answer = tokenizer.convert_tokens_to_string(
            tokenizer.convert_ids_to_tokens(
                inputs["input_ids"][0][start:end]
            )
        )
        return answer
    
    INVALID_ANSWERS = {'[CLS]', '[SEP]', '[PAD]', '[UNK]', ''}

    for i, item in df.iterrows():
        specie_found = item[previous_step_check]

        if specie_found.startswith("No"):
            # Use the BioBERT pipeline to answer the question
            
            text = item[column_to_evaluate]
            question = 'what species was used in the experiment?'

            result = answer_question(question, text).strip()
            
            #print(f"Row {i}: {result['answer']}")

            if result in INVALID_ANSWERS:
                df.at[i, 'Species_BioBERT'] = "not found"

            else: 
                df.at[i, 'Species_BioBERT'] = result

        else:
            print(f"Row {i}: The species was already found in the previous steps.")

    ## Part B. Changing name to  scientific name and requesting ontology

    for i, item in df.iterrows():
        list_species = item['Species_BioBERT']
        list_species_scientific_name = []

        if isinstance(list_species, str):
            list_species = list_species.split(', ')
            #print(list_species)

            if list_species != []:
            
                #print(list_species)
                scientific_name = "Not found"
                for x in list_species:
                    #print(x)

                    url = f'https://www.ebi.ac.uk/ena/taxonomy/rest/any-name/{x}'
                        #print(url)

                    response = requests.get(url)
                        #print(response.status_code)
                    if response.status_code == 200:
                        data = response.json()
                        #print(data)
                        if data:
                            scientific_name = data[0]['scientificName']
                            tax_id = data[0]['taxId']

                            list_species_scientific_name.append(scientific_name)
                            print(f"Scientific name for {x}: {scientific_name}")

                            ols_url = f"https://www.ebi.ac.uk/ols4/api/search?q={scientific_name}&ontology=ncbitaxon&exact=true"
                            ols_response = requests.get(ols_url).json()

                            if ols_response['response']['numFound'] > 0:
                                term_uri = ols_response['response']['docs'][0]['obo_id']
                                print(f"Connected TaxID {tax_id} to OLS term: {term_uri}")

                                tax_biobert = term_uri

                            else:
                                tax_biobert = "No OLS term identified"

                            df.at[i, 'Species_Scientific_Name_TaxID'] = tax_biobert

                        else:
                            scientific_name = 'Not found'
                            print(f"Scientific name for {x}: {scientific_name}")

                df.at[i, 'Species_Scientific_Name_BioBERT'] = str(list_species_scientific_name)
            else:
                df.at[i, 'Species_Scientific_Name_BioBERT'] = 'Not found'

    end_time = time.time()

    print(f"Execution time BioBERT: {end_time - start_time:.2f} seconds")

    return df


### STEP 3. Evaluating with the LLM

def llm_to_ask(df, model_id, previous_step_check, text_to_evaluate, prompt):
    start_time = time.time()
    df['Species_LLM'] = 'Not found'

    pipe = pipeline("text-generation",
                    model = model_id,
                    torch_dtype = torch.bfloat16,
                    device_map="auto",
                    pad_token_id=128001 
                )
    start_time = time.time()

    
    for row, i in df.iterrows(): 
        
        if str(i[previous_step_check]).startswith("Yes"):
            print(f"The species has been indentified in a previous step.")

        else:
            message = [
                {"role": "system", "content": i[text_to_evaluate]},
                {"role": "user", "content": prompt}, #"Can you tell me which scientific species was used in this study?"},
            ]

            outputs = pipe(message, max_new_tokens = 256)
            response = outputs[0]["generated_text"][-1]["content"]
            clean_response = remove_special_characters(response).lower()
            
            df.at[row, 'Species_LLM'] = clean_response
            print(f"Processed row {row} for species extraction.")

    end_time = time.time()
    print(f"Execution time LLM: {end_time - start_time:.2f} seconds")
    return df


def suggest_name(df, column_to_evaluate, model_id):

    start_time = time.time()
    pipe = pipeline("text-generation",
                    model = model_id,
                    torch_dtype = torch.bfloat16,
                    device_map="auto",
                    pad_token_id=128001 
                )
    start_time = time.time()

    for row, i in df.iterrows():
        values_suggestion = i[column_to_evaluate]
        
        message = [
            {"role": "system", "content": values_suggestion},
            {"role": "user", "content": "Suggest a title for the description passed as context. It should be informative a not loger than 10 words." }, #"Can you tell me which scientific species was used in this study?"},
            ]

        outputs = pipe(message, max_new_tokens = 256)
        response = outputs[0]["generated_text"][-1]["content"]
        clean_response = remove_special_characters(response).lower()
            
        df.at[row, 'Suggested_name'] = clean_response
        print(f"Processed row {row} for species extraction.")

    end_time = time.time()
    print(f"Execution time LLM suggeste name: {end_time - start_time:.2f} seconds")
    
    return df
    


### This funtions is the check point

def matching_values(df, field_name, variables_to_compare, column_to_evaluate):
    count_match_species = 0
    
    for row, i in df.iterrows():
        
        if isinstance(i[field_name], str) and i[field_name].strip() != '':

            real_value = i[field_name]
            response   = i[column_to_evaluate]

            # ── Handle NaN explicitly ──
            if pd.isna(response):
                response = ""
            else:
                response = str(response) if not isinstance(response, str) else response
            # ──────────────────────────

            clean_response      = remove_special_characters(response)
            lower_clean_response = clean_response.lower()

            # ── Fix: lowercase real_value too ──
            if real_value.lower() in lower_clean_response:
                df.at[row, 'Comparison_' + variables_to_compare] = 'Yes'
                count_match_species += 1
            else:
                df.at[row, 'Comparison_' + variables_to_compare] = 'No'
            # ───────────────────────────────────

        else:
            df.at[row, 'Comparison_' + variables_to_compare] = 'No provided'

    return df, count_match_species



### Compile the pipeline all together

def run_complete_pipeline(df, model_id, prompt):
    wk_df = combined_text_in_file(df,["Name", "Purpose", "Description", "Comments"], "text_combined")

    texts = wk_df["text_combined"].fillna("").astype(str).tolist()
    nlp = spacy.load("en_ner_bionlp13cg_md") 

    results = []
    for doc in nlp.pipe(texts):
        results.append(extract_entities(doc))

    wk_df["Entities_SpaCy"] = results   
    wk_df["Species_SpaCy"] = wk_df["Entities_SpaCy"].apply(
        lambda d: d.get("ORGANISM", "Not found") if isinstance(d, dict) else "Not found"
        )

    df_scispacy = run_scispacy_check(wk_df)
    df_scispacy, count_match_species_scispacy = matching_values(df_scispacy, "species", "Scispacy_vs_real_species", "Species_Scientific_Name_SciSpacy")

    df_biobert = run_biobert(df_scispacy, "Comparison_Scispacy_vs_real_species", "text_combined")
    df_biobert, count_match_species_biobert = matching_values(df_biobert,"species", "BioBert_vs_real_species", "Species_Scientific_Name_BioBERT")

    df_LLM = llm_to_ask(df_biobert, model_id, "Comparison_BioBert_vs_real_species", "text_combined", prompt)
    df_LLM, count_match_species_llm = matching_values(df_LLM, "species", "LLM_vs_real_species", "Species_LLM")

    return df, count_match_species_scispacy, count_match_species_biobert, count_match_species_llm




def write_output(csv_file, output_df, small_output):
    try:
        output_df.to_csv(csv_file, index=False)
        print(f"Written output to {csv_file}")
        print(small_output)
    except Exception as e:
        print(f"Error writing output: {e}")


# **************************************** IMPLEMENTATION **********************************************************

class Tee:
    """Writes output to both terminal and file simultaneously."""
    def __init__(self, file):
        self.file = file
        self.terminal = sys.stdout
    def write(self, message):
        self.terminal.write(message)  # terminal
        self.file.write(message)      # file
    def flush(self):
        self.terminal.flush()
        self.file.flush()

def main():
    with open('output.txt', 'w') as out_f:
        sys.stdout = Tee(out_f)  # prints go to both terminal and file

        start_time = time.time()
        
        try:
            with open('config_file_pipeline.json') as config_f:
                config = json.load(config_f)

            csv_file = config['csv_file']
            model_id = config['model_id']
            prompt = config['prompt_llm']
            output_csv_file = config['output_csv_file']

            df = load_data(csv_file)
            wk_df = combined_text_in_file(df,["Name", "Purpose", "Description", "Comments"], "text_combined")

            df_complete, count_match_species_scispacy, count_match_species_biobert, count_match_species_llm = run_complete_pipeline(wk_df, model_id, prompt)

            #df_complete = suggest_name(df_LLM, "text_combined", model_id)

            small_output = f"Count match species Spacy: {count_match_species_scispacy}. Count match species BioBERT: {count_match_species_biobert}. Count match species LLM: {count_match_species_llm}."

            write_output(output_csv_file, df_complete, small_output)
            #write_output(output_csv_file, df_complete, small_output)

            end_time = time.time()
            print(f"Total execution time: {end_time - start_time:.2f} seconds")


        finally:
            sys.stdout = sys.__stdout__  # always restore terminal, even if error occurs

if __name__ == "__main__":
    main()