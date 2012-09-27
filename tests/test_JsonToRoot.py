from gnomon.JsonToROOT import JsonToRootConverter
from unittest import TestCase
import validictory
import json

schema = {
    "$schema": "http://json-schema.org/draft-03/schema#",
    "id": "http://json-schema.org/draft-03/schema#",
    "type": "object",

    "properties": {
        "type": {
            "type": ["string", "array"],
            "items": {
                "type": ["string", {"$ref": "#"}]
            },
            "uniqueItems": True,
            "default": "any"
        },

        "properties": {
            "type": "object",
            "additionalProperties": {"$ref": "#"},
            "default": {}
        },

        "patternProperties": {
            "type": "object",
            "additionalProperties": {"$ref": "#"},
            "default": {}
        },

        "additionalProperties": {
            "type": [{"$ref": "#"}, "boolean"],
            "default": {}
        },

        "items": {
            "type": [{"$ref": "#"}, "array"],
            "items": {"$ref": "#"},
            "default": {}
        },

        "additionalItems": {
            "type": [{"$ref": "#"}, "boolean"],
            "default": {}
        },

        "required": {
            "type": "boolean",
            "default": False
        },

        "dependencies": {
            "type": "object",
            "additionalProperties": {
                "type": ["string", "array", {"$ref": "#"}],
                "items": {
                    "type": "string"
                }
            },
            "default": {}
        },

        "minimum": {
            "type": "number"
        },

        "maximum": {
            "type": "number"
        },

        "exclusiveMinimum": {
            "type": "boolean",
            "default": False
        },

        "exclusiveMaximum": {
            "type": "boolean",
            "default": False
        },

        "minItems": {
            "type": "integer",
            "minimum": 0,
            "default": 0
        },

        "maxItems": {
            "type": "integer",
            "minimum": 0
        },

        "uniqueItems": {
            "type": "boolean",
            "default": False
        },

        "pattern": {
            "type": "string",
            "format": "regex"
        },

        "minLength": {
            "type": "integer",
            "minimum": 0,
            "default": 0
        },

        "maxLength": {
            "type": "integer"
        },

        "enum": {
            "type": "array",
            "minItems": 1,
            "uniqueItems": True
        },

        "default": {
            "type": "any"
        },

        "title": {
            "type": "string"
        },

        "description": {
            "type": "string"
        },

        "format": {
            "type": "string"
        },

        "divisibleBy": {
            "type": "number",
            "minimum": 0,
            "exclusiveMinimum": True,
            "default": 1
        },

        "disallow": {
            "type": ["string", "array"],
            "items": {
                "type": ["string", {"$ref": "#"}]
            },
            "uniqueItems": True
        },

        "extends": {
            "type": [{"$ref": "#"}, "array"],
            "items": {"$ref": "#"},
            "default": {}
        },

        "id": {
            "type": "string",
            "format": "uri"
        },

        "$ref": {
            "type": "string",
            "format": "uri"
        },

        "$schema": {
            "type": "string",
            "format": "uri"
        }
    },

    "dependencies": {
        "exclusiveMinimum": "minimum",
        "exclusiveMaximum": "maximum"
    },

    "default": {}
}

class TestLogging(TestCase):
    def setUp(self):
        file_data = open('EventSchema.json').read()
        self.my_schema = json.loads(file_data)
        self.converter = JsonToRootConverter(self.my_schema)

    def test_setup(self):
        file_data = json.loads(open('Event.json').read())
        for i in range(100):
            self.converter.Process(file_data)
        self.converter.Shutdown()
        raise ValueError()

    def test_schema_schema(self):
        validictory.validate(schema, schema, required_by_default=False)

    def test_schema(self):
        validictory.validate(self.my_schema, schema, required_by_default=False)
