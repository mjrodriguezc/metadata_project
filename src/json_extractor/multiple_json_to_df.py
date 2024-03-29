import pandas as pd
import os
import json

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
