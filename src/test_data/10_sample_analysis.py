import json
import os
import descrite_analysis_module 
import Unit_test_descriptive_analysis

# Set the working directory
os.chdir('PATH')

file_list =["1153.json", "2842.json", "3492.json", "3638.json","3647.json", "3648.json",
            "10010.json", "10040.json", "10060.json", "17264.json", "19235.json"]


def read_multiple_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

if __name__ == "__main__":
    json_files = file_list

    file_contents = {}

    for json_file in json_files:
        content = read_multiple_json_file(json_file)
        file_contents[json_file] = content

print(file_contents)
file1 = descrite_analysis_module.json_to_data("1153.json", file_contents)
print(file1)

missing_file1 = descrite_analysis_module.missing_values_table(file1)
print(missing_file1)

