import unittest
from descrite_analysis_module import json_to_data
import os
import pandas as pd
import json

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

class TestJsonToDataFunction(unittest.TestCase):

    def test_empty_dictionary(self):
        result = json_to_data("1153.json", file_contents)
        self.assertEqual("The file is empty", (0, 0))

    def test_invalid_id_type(self):
        result = json_to_data(123, file_contents)
        self.assertEqual("You must provide a string", (0, 0))

    def test_invalid_id(self):
        result = json_to_data("1153.json", file_contents)
        self.assertEqual("The ID is invalid", (0, 0))

if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
