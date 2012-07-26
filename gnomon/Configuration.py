"""Manage the configuration files

This class is used within gnomon to tell various classes how to configure
themselves.  Each Configuration class will generate or retrieve a JSON
file that is used afterwards by various other classes."""


import os
import inspect
import logging
import random
import sys
import json
import validictory


def fetch_config_config(filename):
    """Fetch configuration file for the configuration class

    Loads the JSON and converts to a dictionary that is returned"""

    #  This trick gets the directory of *this* file Configuration.py thus
    # allowing to find the schema files relative to this file.
    dir_name = os.path.dirname(inspect.getfile(inspect.currentframe()))

    # Append json
    filename = os.path.join('json', filename)

    fileobj = open(os.path.join(dir_name, filename), 'r')
    my_dict = json.loads(fileobj.read())
    return my_dict


def populate_args(parser):
    """Add commandline arguments to parser from schema
    """
    schema = fetch_config_config('ConfigurationSchema.json')
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
            if value['type'] == 'number':
                parser.add_argument(arg, help=desc, type=float)
            if value['type'] == 'integer':
                parser.add_argument(arg, help=desc, type=int)


class ConfigurationBase():
    """Base class for all configuration classes"""

    def __init__(self, name, run, overload=None):  # pylint: disable-msg=W0613
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

        if run == 0:
            run = random.randint(1, sys.maxint)
            self.log.warning('Random run number %d since none specified', run)

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

        self.json = config_json

    def get_configuration_dict(self):
        """Return dictionary of the JSON config
        """
        return self.json


class LocalConfiguration(ConfigurationBase):
    """Configuration fetched from disk"""

    def __init__(self, name, run=0, overload=None):
        """Setup the CouchDB configuration manager.

        The default connection is to localhost's port 5984.  This can be
        overridden by setting the environmental variable COUCHDB_URL to,
        for example, http://new_server:1234/"""

        ConfigurationBase.__init__(self, name, run)

        defaults = fetch_config_config('ConfigurationDefaults.json')

        if overload:
            for key, val in overload.iteritems():
                if val is not None:
                    defaults[key] = val

        self.set_json(defaults)

DEFAULT = LocalConfiguration
GLOBAL_CONFIG = None
