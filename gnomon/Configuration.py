"""Manage how gnomon configures itself and its proceesors

This class is used within gnomon to tell various classes how to configure
themselves.  Each Configuration class will generate or retrieve a JSON
file that is used afterwards by various other classes.

Any proposed configuration JSON file is compared against a configuration schema.  The schema requires certain attributes
be specified in order to start gnomon.  The schema checker is forgiving in that new configuration keys are allowed
without changing the schema; the schema only requires certain things be defined, it doesn't prevent you from defining
new things.

Any new configuration must inherit from ConfigurationBase.

"""

import os
import inspect
import random
import sys
import json
import validictory

# Note: Do not use the python logging library!  This class gets called before
# the loggers are setup.




class ConfigurationBase(object):
    """Base class for all configuration classes

    If the run number is zero, replace it with a random run number"""

    def __init__(self, name, run, overload=None):  # pylint: disable-msg=W0613
        if run == 0:
            run = random.randint(1, sys.maxint)

        self.name = name
        self.run = run

        self.configuration_dict = None

    def set_json(self, config_json):
        """Permanently set the JSON configuration

        Unable to call twice."""

        if self.configuration_dict is not None:
            raise RuntimeError("Can only set configuration once", self.configuration_dict)

        schema = fetch_config('ConfigurationSchema.json')
        validictory.validate(config_json, schema)

        config_json['name'] = self.name
        config_json['run_number'] = self.run
        config_json['src_dir'] = get_source_dir()
        config_json['data_dir'] = get_data_dir()
        config_json['log_dir'] = get_log_dir()

        self.configuration_dict = config_json


class LocalConfiguration(ConfigurationBase):
    """Read a configuration from disk and overload if necessary
    """

    def __init__(self, name, run=0, overload=None,
                 filename='ConfigurationDefaults.json'):
        ConfigurationBase.__init__(self, name, run)

        defaults = fetch_config(filename)

        if overload:
            for key, val in overload.iteritems():
                if val is not None:
                    defaults[key] = val

        self.set_json(defaults)


class MockConfiguration(LocalConfiguration):
    """Mock configuration for testing

    This is just a copy of LocalConfiguration for now
    """
    pass


def get_configuration_dict():
    """Return configuration as a dictionary
    """
    return self.configuration_dict


def get_source_dir():
    """Find where the truth path to the directory containing the Configuration module source code

    It can be useful to know the full path to the Configuration module's source code in order to try to guess where the
    data and log files are stored.  It does this by inspecting the current running python instance."""

    #  This trick gets the directory of *this* file Configuration.py thus
    # allowing to find the schema files relative to this file.
    return os.path.dirname(inspect.getfile(inspect.currentframe()))


def get_data_dir():
    """Find the data directory that stores geometries, cross sections, etc."""
    src_dir = get_source_dir()
    return os.path.join(src_dir, '../data')


def get_log_dir():
    """Find the directory used for saving log files"""
    src_dir = get_source_dir()
    return os.path.join(src_dir, '../log')


def fetch_config(filename):
    """Fetch the Configuration schema information

    Finds the schema file, loads the file and reads the JSON, then converts to a dictionary that is returned
    """

    #  This trick gets the directory of *this* file Configuration.py thus
    # allowing to find the schema files relative to this file.
    dir_name = get_source_dir()

    # Append json
    filename = os.path.join('json', filename)

    fileobj = open(os.path.join(dir_name, filename), 'r')
    my_dict = json.loads(fileobj.read())
    return my_dict


def populate_args(parser):
    """Add commandline arguments to parser from schema
    """
    schema = fetch_config('ConfigurationSchema.json')

    populate_args_level(schema, parser)


def populate_args_level(schema, parser):
    """Use a schema to populate a command line argument parser"""
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


DEFAULT = LocalConfiguration
GLOBAL_CONFIG = None
RUNTIME_CONFIG = {}
