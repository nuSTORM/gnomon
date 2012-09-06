"""Manage the configuration files

This class is used within gnomon to tell various classes how to configure
themselves.  Each Configuration class will generate or retrieve a JSON
file that is used afterwards by various other classes."""


import os
import inspect
import random
import sys
import tempfile
import json
import validictory
from array import array

# Note: Do not use the python logging library!  This class gets called before
# the loggers are setup.


def get_source_dir():
    #  This trick gets the directory of *this* file Configuration.py thus
    # allowing to find the schema files relative to this file.
    return os.path.dirname(inspect.getfile(inspect.currentframe()))


def get_data_dir():
    src_dir = get_source_dir()
    return os.path.join(src_dir, '../data')


def get_log_dir():
    src_dir = get_source_dir()
    return os.path.join(src_dir, '../log')


def fetch_config_config(filename):
    """Fetch configuration file for the configuration class

    Loads the JSON and converts to a dictionary that is returned"""

    #  This trick gets the directory of *this* file Configuration.py thus
    # allowing to find the schema files relative to this file.
    dir_name = get_source_dir()

    # Append json
    filename = os.path.join('json', filename)

    fileobj = open(os.path.join(dir_name, filename), 'r')
    my_dict = json.loads(fileobj.read())
    return my_dict


def populate_args_level(schema, parser):
    """ Populate just one node in a tree; can be recursive"""
    for key, value in schema['properties'].iteritems():
        if key == 'name':
            continue

        arg = '--%s' % key
        desc = value['description']

        if 'type' in value:
            if value['type'] == 'string':
                if 'enum' in value:
                    parser.add_argument(arg, help=desc, type=str,
                                        choices=value['enum'])
                else:
                    parser.add_argument(arg, help=desc, type=str)
            elif value['type'] == 'number':
                parser.add_argument(arg, help=desc, type=float)
            elif value['type'] == 'integer':
                parser.add_argument(arg, help=desc, type=int)
            elif str(value['type']) == 'array':
                assert value['minItems'] == value['maxItems']

                if value['items']['type'] != 'number':
                    raise NotImplementedError("Only float arrays work")
                parser.add_argument(arg, help=desc, type=float,
                                    nargs=value['maxItems'], metavar='N')
            elif value['type'] == 'object':
                #group = parser.add_argument_group(key, value['description'])
                #populate_args_level(value, group)
                pass


def populate_args(parser):
    """Add commandline arguments to parser from schema
    """
    schema = fetch_config_config('ConfigurationSchema.json')

    populate_args_level(schema, parser)


class ConfigurationBase():
    """Base class for all configuration classes"""

    def __init__(self, name, run, overload=None):  # pylint: disable-msg=W0613
        if run == 0:
            run = random.randint(1, sys.maxint)

        self.name = name
        self.run = run

        self.json = None

    def set_json(self, config_json):
        """Fix the JSON configuration

        Unable to call twice"""

        if self.json is not None:
            raise RuntimeError("Can only set configuration once", self.json)

        schema = fetch_config_config('ConfigurationSchema.json')
        validictory.validate(config_json, schema)

        config_json['name'] = self.name
        config_json['run_number'] = self.run
        config_json['src_dir'] = get_source_dir()
        config_json['data_dir'] = get_data_dir()
        config_json['log_dir'] = get_log_dir()

        self.json = config_json

    def get_configuration_dict(self):
        """Return dictionary of the JSON config
        """
        return self.json


class LocalConfiguration(ConfigurationBase):
    """Configuration fetched from disk"""

    def __init__(self, name, run=0, overload=None,
                 filename='ConfigurationDefaults.json'):
        """Setup the CouchDB configuration manager.

        The default connection is to localhost's port 5984.  This can be
        overridden by setting the environmental variable COUCHDB_URL to,
        for example, http://new_server:1234/"""

        ConfigurationBase.__init__(self, name, run)

        defaults = fetch_config_config(filename)

        if overload:
            for key, val in overload.iteritems():
                if val is not None:
                    defaults[key] = val

        self.set_json(defaults)

class MockConfiguration(LocalConfiguration):
    """Mock configuration for testing

    This is just a reference to LocalConfiguration for now
    """
    pass

        

DEFAULT = LocalConfiguration
GLOBAL_CONFIG = None
RUNTIME_CONFIG = {}
