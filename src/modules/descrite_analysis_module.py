
import pandas as pd
import os
import json

### Get the file

def get_test_file (name):

    test_data_path = "PATH"
    test_file = os.path.join(test_data_path,name)
    return test_file

############### For MULTIPLE files analysis ###############


# Convert several json files to dataframe

def json_files_to_df (ID, dicctionary):
    working_df = pd.DataFrame()

    if len(dicctionary) == 0:
        print("The file is empty")
    
    elif not isinstance(ID, str):
        print("You must provide a string")

    else:

        if ID not in dicctionary:
            print ("The ID is invalid")
        
        else:
            data = dicctionary[ID]
            df_generalDesc = pd.json_normalize(data['generalDesc'])
            df_contributionDesc_authors = pd.json_normalize(data['contributionDesc']['authors'])
            df_curators = pd.json_normalize(data['contributionDesc']['curators'])
            df_institutions = pd.json_normalize(data['contributionDesc']['institutions'])
            df_fundings = pd.json_normalize(data['contributionDesc']['fundings'])
            df_experimentalDetails = pd.json_normalize(data['experimentalDetails'])
            df_characteristics = pd.json_normalize(data['characteristic'])
            df_bioDescrip = pd.json_normalize(data['bioDescription'])
            df_summary = pd.json_normalize(data['bioSummary'])
            df_provenance = pd.json_normalize(data['provenance'])
            
            df_institutions = df_institutions.rename(columns={'name':'institution_name','longName':'logName'})
            
            working_df = pd.concat([df_generalDesc, df_contributionDesc_authors, df_curators,
                            df_institutions, df_fundings, df_experimentalDetails, df_characteristics,
                            df_bioDescrip, df_summary, df_provenance], axis=1)
            
            working_df['species'] = data['species']
            working_df['dataCategory'] = data['dataCategory']
            working_df['id_experiment'] = data['id']
    
    return working_df

# Get the reads

def reads_correctly_multiple_json_files(name):
    file = get_test_file(name)
    data = json_files_to_df(file)
    return data

## Fine missing values in a dataframe per column

def missing_values_table(df):
    mis_val = df.isnull().sum()
    mis_val_percent = 100 * df.isnull().sum() / len(df)
    mis_val_table = pd.concat([mis_val, mis_val_percent], axis=1)
    mis_val_table_ren_columns = mis_val_table.rename(
        columns={0: 'Missing Values', 1: '% of Total Values'})
    return mis_val_table_ren_columns

## Counting the words in the field

def number_of_words(row_header, df, lista):
    for value in df[row_header]:
        phrase = value.split()
        words_count = len(phrase)
        lista.append(words_count)
    return lista

## Counting the chracters in the field

def character_long (new_list, row_header,df):
    for value in len(df):
        valor = len(df[row_header][value])
        new_list.append(valor)
    return new_list




############### For SINGLE analysis ###############

# Get dataframe from one json file
def json_to_df (file):
    json_file = open(file)
    json_dicc = json.load(json_file)
    df_generalDesc = pd.json_normalize(json_dicc['generalDesc'])
    df_contributionDesc_authors = pd.json_normalize(json_dicc ['contributionDesc']['authors'])
    df_curators = pd.json_normalize(json_dicc ['contributionDesc']['curators'])
    df_institutions = pd.json_normalize(json_dicc ['contributionDesc']['institutions'])
    df_fundings = pd.json_normalize(json_dicc ['contributionDesc']['fundings'])
    df_experimentalDetails = pd.json_normalize(json_dicc ['experimentalDetails'])
    df_characteristics = pd.json_normalize(json_dicc ['characteristic'])
    df_bioDescrip = pd.json_normalize(json_dicc ['bioDescription'])
    df_summary = pd.json_normalize(json_dicc ['bioSummary'])
    df_provenance = pd.json_normalize(json_dicc ['provenance'])
            
    df_institutions = df_institutions.rename(columns={'name':'institution_name','longName':'logName'})
            
    working_df = pd.concat([df_generalDesc, df_contributionDesc_authors, df_curators,
                            df_institutions, df_fundings, df_experimentalDetails, df_characteristics,
                            df_bioDescrip, df_summary, df_provenance], axis=1)
            
    working_df['species'] = json_dicc ['species']
    working_df['dataCategory'] = json_dicc ['dataCategory']
    working_df['id_experiment'] = json_dicc ['id']

    return working_df

# Get reads
def reads_correctly_one_json_file(name):
    file = get_test_file(name)
    data = json_to_df(file)
    return data

# Functions
def number_of_words_single(df, row_name, position):
    words = df[row_name][position].split()
    return len(words)


