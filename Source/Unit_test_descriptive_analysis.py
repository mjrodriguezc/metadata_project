import unittest
from descrite_analysis_module import json_to_data
import os

os.chdir('/Users/s2531396/Library/CloudStorage/OneDrive-UniversityofEdinburgh/PhD/Code')

file = open('19235.json')

class MyTestCase(unittest.TestCase):
    def test_json_to_data(self):
        result = json_to_data("14.json", file)
        self.assertEqual(result)



