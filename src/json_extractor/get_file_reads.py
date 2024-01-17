import pandas as pd
import os
import json

### Get file
def get_test_file (name):

    test_data_path = "/Users/s2531396/Library/CloudStorage/OneDrive-UniversityofEdinburgh/PhD/Code"
    test_file = os.path.join(test_data_path,name)
    return test_file


### Get reads

def reads_correctly_multiple_json_files(name):
    file = get_test_file(name)
    data = json_files_to_df(file)
    return data
