import pandas as pd
import json
import os
from collections import Counter
import numpy as np
import scispacy
import spacy
import matplotlib.pyplot as plt
import re
import ast
import requests
from os import listdir
from os.path import isfile, join
from functools import reduce
import time
import contextlib
import sys
from functools import lru_cache


### NLP task packages
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


### Models implementation packages
from transformers import pipeline
import torch

from transformers import AutoModelForQuestionAnswering, AutoTokenizer


### Efficiency
from concurrent.futures import ThreadPoolExecutor, as_completed

# ***************************************** LOAD THE MODELS *********************************************************


#@st.cache_resource
def load_spacy_model():
    return spacy.load("en_ner_bionlp13cg_md")

#@st.cache_resource
def load_biobert_model():
    model_name = "dmis-lab/biobert-large-cased-v1.1-squad"
    tokenizer  = AutoTokenizer.from_pretrained(model_name)
    model      = AutoModelForQuestionAnswering.from_pretrained(model_name).to("cuda")
    return tokenizer, model

#@st.cache_resource
def load_llm_pipeline(model_id, value_tokens):
    return pipeline("text-generation", model=model_id,
                    torch_dtype=torch.bfloat16, device_map="auto", pad_token_id=128001, max_new_tokens=value_tokens)


# **************************************** PRE PROCESSING  **********************************************************

#@contextlib.contextmanager
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

# **************************************** FUNCTIONS **********************************************************

##### Species extraction

def extract_species_from_existing_text(text):
    nlp = load_spacy_model() 
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

# API call for species
#@lru_cache(maxsize=512)
def lookup_taxonomy(name: str):
    url      = f'https://www.ebi.ac.uk/ena/taxonomy/rest/any-name/{name}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]['scientificName'], data[0]['taxId']
    return None, None

# API call for ols
#@lru_cache(maxsize=512)
def lookup_ols(scientific_name: str):
    url      = f"https://www.ebi.ac.uk/ols4/api/search?q={scientific_name}&ontology=ncbitaxon&exact=true"
    response = requests.get(url).json()
    if response['response']['numFound'] > 0:
        return response['response']['docs'][0]['obo_id']
    return "No OLS term identified"

# For efficiency
def lookup_full(name: str):
    """Single function that does both API calls for one species name."""
    scientific_name, tax_id = lookup_taxonomy(name)
    if scientific_name:
        term_uri = lookup_ols(scientific_name)
        return name, (scientific_name, str(tax_id), term_uri)
    return name, (None, None, None)





# **************************************** PIPELINE **********************************************************
### STEP 1. SciSpacy

#def run_scispacy_check(df):
    df['Species_Scientific_Name_SciSpacy'] = 'Not found'
    df['Species_Scientific_Name_TaxID'] = 'None'
    df['Species_Scientific_Name_OLS'] = 'None'

    start_time = time.time()
        
    for i, item in df.iterrows():
        list_species_spacy = item['Species_SpaCy']

        if not isinstance(list_species_spacy, list) or not list_species_spacy:
            continue

        found_names = []
        found_taxids = []
        found_ols = []

        for x in list_species_spacy:
            for unique_value in x.split(' '):
                scientific_name, tax_id = lookup_taxonomy(unique_value)

                if scientific_name:
                    term_uri = lookup_ols(scientific_name)
                    found_names.append(scientific_name)
                    found_taxids.append(str(tax_id))
                    found_ols.append(term_uri)
                    print(f"Scientific name for {unique_value}: {scientific_name} → {term_uri}")
                else:
                    print(f"Scientific name for {unique_value}: Not found")

        if found_names:
            df.at[i, 'Species_Scientific_Name_SciSpacy'] = str(found_names)
            df.at[i, 'Species_Scientific_Name_TaxID'] = str(found_taxids)
            df.at[i, 'Species_Scientific_Name_OLS'] = str(found_ols)

    print(f"Execution time SciSpacy: {time.time() - start_time:.2f} seconds")
    return df


def run_scispacy_check(df, max_workers=10):
    df['Species_Scientific_Name_SciSpacy'] = 'Not found'
    start_time = time.time()

    # ── Phase 1: Collect ALL unique values first (no API calls yet) ──
    all_unique_values = set()
    for i, item in df.iterrows():
        list_species_spacy = item['Species_SpaCy']
        if not isinstance(list_species_spacy, list) or not list_species_spacy:
            continue
        for x in list_species_spacy:
            for unique_value in x.split(' '):
                all_unique_values.add(unique_value)

    print(f"Found {len(all_unique_values)} unique values to look up.")

    # ── Phase 2: Look them all up IN PARALLEL ────────────────────────
    taxonomy_cache = {}  # name -> (scientific_name, tax_id, term_uri)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(lookup_full, name): name
            for name in all_unique_values
        }
        for future in as_completed(futures):
            name        = futures[future]
            name, result = future.result()
            taxonomy_cache[name] = result
            scientific_name, tax_id, term_uri = result
            if scientific_name:
                print(f"✔ {name} → {scientific_name} ({term_uri})")
            else:
                print(f"✘ {name} → Not found")

    print(f"Parallel lookup complete. Assigning results to dataframe...")

    # ── Phase 3: Assign results back (no API calls, uses cache) ──────
    for i, item in df.iterrows():
        list_species_spacy = item['Species_SpaCy']
        if not isinstance(list_species_spacy, list) or not list_species_spacy:
            continue

        found_names  = []
        found_taxids = []
        found_ols    = []

        for x in list_species_spacy:
            for unique_value in x.split(' '):
                scientific_name, tax_id, term_uri = taxonomy_cache.get(
                    unique_value, (None, None, None)
                )
                if scientific_name:
                    found_names.append(scientific_name)
                    found_taxids.append(tax_id)
                    found_ols.append(term_uri)

        if found_names:
            df.at[i, 'Species_Scientific_Name_SciSpacy'] = str(found_names)
            df.at[i, 'Species_Scientific_Name_TaxID'] = str(found_taxids)
            df.at[i, 'Species_Scientific_Name_OLS'] = str(found_ols)

    print(f"Execution time SciSpacy: {time.time() - start_time:.2f} seconds")
    return df


### 2. STEP 2: BioBERT

#def run_biobert(df, previous_step_check, column_to_evaluate):

    # Load the BioBERT model and create a pipeline for question answering
    df['Species_BioBERT'] = df.get('Species_BioBERT', 'Not found')
    start_time = time.time()

    tokenizer, model = load_biobert_model() 

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

def run_biobert(df, previous_step_check, column_to_evaluate, max_workers=10):

    # ✅ Cleaner column initialisation
    if 'Species_BioBERT' not in df.columns:
        df['Species_BioBERT'] = 'Not found'

    start_time  = time.time()
    tokenizer, model = load_biobert_model()
    INVALID_ANSWERS  = {'[CLS]', '[SEP]', '[PAD]', '[UNK]', ''}

    def answer_question(question, context):
        inputs = tokenizer(
            question, context,
            return_tensors="pt", truncation=True, max_length=256
        ).to("cuda")

        with torch.no_grad():
            outputs = model(**inputs)
        start  = torch.argmax(outputs.start_logits)
        end    = torch.argmax(outputs.end_logits) + 1

        answer = tokenizer.convert_tokens_to_string(
            tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][start:end])
        ).strip()
        return answer

    # ── Part A: BioBERT inference (sequential — GPU bound) ──────────
    print("--- Part A: BioBERT inference ---")
    for i, item in df.iterrows():
        specie_found = item[previous_step_check]
        if specie_found.startswith("No"):
            result = answer_question(
                'what species was used in the experiment?',
                item[column_to_evaluate]
            )
            df.at[i, 'Species_BioBERT'] = "Not found" if result in INVALID_ANSWERS else result
            print(f"Row {i}: BioBERT → {df.at[i, 'Species_BioBERT']}")
        else:
            print(f"Row {i}: Species already found in previous step.")

    # ── Part B: Resolve to scientific names via API (parallel) ───────
    print("--- Part B: Taxonomy lookup ---")

    # Phase 1: Collect all unique species names from BioBERT results
    all_unique_species = set()
    for i, item in df.iterrows():
        list_species = item['Species_BioBERT']
        if isinstance(list_species, str) and list_species.lower() != 'not found':
            for x in list_species.split(', '):
                all_unique_species.add(x.strip())

    print(f"Found {len(all_unique_species)} unique species to look up.")

    # Phase 2: Look them all up in parallel
    taxonomy_cache = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(lookup_full, name): name
            for name in all_unique_species
        }
        for future in as_completed(futures):
            name, result = future.result()
            taxonomy_cache[name] = result
            scientific_name, tax_id, term_uri = result
            if scientific_name:
                print(f"✔ {name} → {scientific_name} ({term_uri})")
            else:
                print(f"✘ {name} → Not found")

    print("Parallel lookup complete. Assigning results to dataframe...")

    # Phase 3: Assign results back to dataframe
    df['Species_Scientific_Name_BioBERT'] = 'Not found'

    for i, item in df.iterrows():
        list_species = item['Species_BioBERT']

        # Skip rows where BioBERT found nothing
        if not isinstance(list_species, str) or list_species.lower() == 'not found':
            continue

        found_names  = []
        found_taxids = []
        found_ols    = []

        for x in list_species.split(', '):
            scientific_name, tax_id, term_uri = taxonomy_cache.get(
                x.strip(), (None, None, None)
            )
            if scientific_name:
                found_names.append(scientific_name)
                found_taxids.append(tax_id)
                found_ols.append(term_uri)

        if found_names:
            df.at[i, 'Species_Scientific_Name_BioBERT'] = str(found_names)
            df.at[i, 'Species_Scientific_Name_TaxID']   = str(found_taxids)
            df.at[i, 'Species_Scientific_Name_OLS']     = str(found_ols)

    print(f"Execution time BioBERT: {time.time() - start_time:.2f} seconds")
    return df


### STEP 3. Evaluating with the LLM

def llm_to_ask(df, model_id, previous_step_check, text_to_evaluate, prompt):
    start_time = time.time()
    df['Species_LLM'] = 'Not found'

    pipe = load_llm_pipeline(model_id, 256)
    pipe.model.generation_config.max_length = None
    start_time = time.time()

    for row, i in df.iterrows(): 
        
        scispacy_ok = str(i.get('Comparison_Scispacy_vs_real_species', 'No'))
        biobert_ok  = str(i[previous_step_check])

        if scispacy_ok.startswith("No") and biobert_ok.startswith("No"):

            message = [
                {"role": "system", "content": i[text_to_evaluate]},
                {"role": "user", "content": prompt}, #"Can you tell me which scientific species was used in this study?"},
            ]

            outputs = pipe(message, max_new_tokens = 256)
            response = outputs[0]["generated_text"][-1]["content"]
            clean_response = remove_special_characters(response).lower()
            
            df.at[row, 'Species_LLM'] = clean_response
            print(f"Processed row {row} for species extraction.")

        else:
            print(f'The species has been identified in a previous step.')

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


# **** Standardize values from dataframe **********





# ******************************************** Study type *******************************************************

def study_type_prediction(df, field, prompt, model_id, client):

    wk_field = str(df[field])
    all_possible_options = list(wk_field)

    for row, i in df.itterow():

        prompt_complete = prompt + "Choose only one possible option from this list and justify your choice: " + str(all_possible_options)

        if "Llama" or "Mistral" in model_id:

            pipe = load_llm_pipeline(model_id, 256)
            pipe.model.generation_config.max_length = None

            message = [
                        {"role": "system", "content":"This is your context: " + str(df.at[row, "text_combined"])},
                        {"role": "user", "content": prompt_complete}, #"Can you tell me which scientific species was used in this study?"},
                    ]

            outputs = pipe(message)
            response = outputs[0]["generated_text"][-1]["content"]
            clean_response = remove_special_characters(response).lower()


        if "gpt" or "GPT" in model_id:
        
            response = client.chat.completions.create(
                model=model_id,  # use a real model id you have access to
                messages=[
                    {"role": "system", "content": "This is your context: " + str(df.at[row, "text_combined"])},
                    {"role": "user", "content": "Based on the context provided, give me the name of three scientific species that could be used in this study. If you don't know, say 'I don't know'."}
                ],
            )

            clean_response = response.choices[0].message.content
                    
        df.at[row, 'Study_type_LLM'] = clean_response
        print(f"Processed row {row} for species extraction.")


    return df





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
            prompt_species = config['prompt_llm']
            prompt_study_type = config['prompt_study_type']
            output_csv_file = config['output_csv_file']
            field_to_evalute = config['field_to_evaluate']

            df = load_data(csv_file)
            wk_df = combined_text_in_file(df,["Name", "Purpose", "Description", "Comments"], "text_combined")

            if "species" in field_to_evalute:

                df_complete, count_match_species_scispacy, count_match_species_biobert, count_match_species_llm = run_complete_pipeline(wk_df, model_id, prompt_species)
                #df_complete = suggest_name(df_LLM, "text_combined", model_id)
                small_output = f"Count match species Spacy: {count_match_species_scispacy}. Count match species BioBERT: {count_match_species_biobert}. Count match species LLM: {count_match_species_llm}."

                write_output(output_csv_file, df_complete, small_output)
                #write_output(output_csv_file, df_complete, small_output)

                end_time = time.time()
                print(f"Total execution time: {end_time - start_time:.2f} seconds")

            if "study" in field_to_evalute:
                df_complete = study_type_prediction(df, field_to_evalute, prompt_study_type, model_id, client)
            
            else: 
                print(f"No valid study type specified.")


        finally:
            sys.stdout = sys.__stdout__  # always restore terminal, even if error occurs

if __name__ == "__main__":
    main()