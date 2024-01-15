import json
import os
import descrite_analysis_module 
import Unit_test_descriptive_analysis

test_path = descrite_analysis_module.get_test_file("1153.json")
test_file = descrite_analysis_module.reads_correctly_one_json_file(test_path)
print(test_file)

words_single = descrite_analysis_module.number_of_words_single(test_file, "name", 0)
print(words_single)


