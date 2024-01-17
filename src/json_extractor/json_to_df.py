import pandas as pd
import os
import json


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
