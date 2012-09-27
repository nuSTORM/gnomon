from gnomon.JsonToROOT import JsonToRootConverter
from unittest import TestCase
import json

class TestLogging(TestCase):
    def test_setup(self):
        file_data = open('EventSChema.json')
        my_schema = json.loads(file_data)
        JsonToRootConverter(my_schema)