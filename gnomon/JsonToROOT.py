"""Create a ROOT file from a Schema and JSON output"""

import ROOT
import logging
from collections import Mapping, Set, Sequence
import validictory

# Maximum buffer size for an array in the ROOT output
BUFFER_SIZE = 1024

class JsonToROOTConverter(object):
    """Convert JSON output to a ROOT file

    Start with a JSON schema which maps keys to their type and also where in the ROOT
    file they should go.  Then get passed each event.  There are two main initialization
    events: a struct is created in memory using ROOT and CINT, then a TTree is bound to
    the branches within the struct."""

    def __init__(self, schema):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

        self.schema = schema

        #  Create ROOT file and TTree
        filename = 'gnomon.root'
        self.file = ROOT.TFile(filename, 'RECREATE')
        self.t = ROOT.TTree('t', '')

         # This code will be passed into CINT
        self.names_lookup, self.types_lookup = self.make_lookups(schema)
        my_struct_code = self.form_cint(self.names_lookup, self.types_lookup)

        self.log.info('Using following structure for converting Python: %s' %  my_struct_code)
        
        ROOT.gROOT.ProcessLine(my_struct_code)

        from ROOT import MyStruct

        self.my_struct = MyStruct()

        for key, val in self.names_lookup.iteritems():
            name = val
            my_type = self.types_lookup[key]

            code = None
            if my_type == 'string':
                code = 'C'
            elif my_type == 'integer':
                code = 'I'
            elif my_type == 'number' or my_type == 'array':
                code = 'F'
            elif my_type == 'object':
                pass
            elif my_type == 'boolean':
                code = 'O'
            else:
                raise ValueError

            x = ROOT.AddressOf(self.my_struct, str(name))
            if my_type == 'array':
                self.t.Branch(name, x,  '%s[%d]/%s' % (name, BUFFER_SIZE, code))
            else:
                self.t.Branch(name, x,  '%s/%s' % (name, code))

    def Process(self, doc):
        try:
            validictory.validate(doc, self.schema, required_by_default=False)
        except:
            raise
        
        default = -99999

        for key in self.names_lookup.values():
            if isinstance(getattr(self.my_struct, key), (float, int)):
                setattr(self.my_struct, key, default)  # not defined, ie. default
            elif isinstance(getattr(self.my_struct, key), (str)):
                setattr(self.my_struct, key, str(-9999))  # not defined, ie. default  
                

        for key, val in self.objwalk(doc):
            if key in self.names_lookup.keys():
                setattr(self.my_struct,
                        self.names_lookup[key],
                        val)

            # check if list
            if len(key) > 1 and isinstance(key[-1], int) and key[0:-1] in self.names_lookup.keys():
                temp = getattr(self.my_struct,
                               self.names_lookup[key[0:-1]])
                temp[key[-1]] = val
                setattr(self.my_struct,
                        self.names_lookup[key[0:-1]],
                        temp)

        self.t.Fill()

    def Shutdown(self):
        self.file.cd()
        self.t.Write("treegnome")
        #self.file.Write()

        self.file.Close()


    def make_lookups(self, my_dict):
        #  This will map paths in the event tree to ROOT variable names
        names_lookup = {}
        types_lookup = {}

        for key, val in self.objwalk(my_dict):
            trunc_key = key[:-1] # trunacte off end

            trunc_key = tuple([x for x in list(trunc_key) if x != 'properties'])

            if key[-1] == 'description':
                names_lookup[trunc_key] = val
            elif key[-1] == 'type':
                types_lookup[trunc_key] = val
            else:
                pass

        self.log.info("Names lookup",  names_lookup)

        return names_lookup, types_lookup

    def form_cint(self, names_lookup, types_lookup):
        my_struct_code = 'struct MyStruct {'

        for key, val in names_lookup.iteritems():
            name = val
            my_type = types_lookup[key]

            if my_type == "string":
                my_struct_code += 'char %s[256];' % name
            elif my_type == "integer":
                my_struct_code += 'int %s;' % name
            elif my_type == "number":
                my_struct_code += 'float %s;' % name
            elif my_type == "boolean":
                my_struct_code += 'bool %s;' % name
            elif my_type == 'array':
                my_struct_code += 'float %s[%d];' % (name, BUFFER_SIZE)

        my_struct_code += '};'

        return my_struct_code

    def objwalk(self, obj, path=(), memo=None):
        """Traverse a dictionary recursively and save path

        Taken from:
  http://code.activestate.com/recipes/577982-recursively-walk-python-objects/
"""

        # dual python 2/3 compatability, inspired by the "six" library
        string_types = (str, unicode) if str is bytes else (str, bytes)
        iteritems = lambda mapping: getattr(mapping, 'iteritems', mapping.items)()

        if memo is None:
            memo = set()
        iterator = None
        if isinstance(obj, Mapping):
            iterator = iteritems
        elif isinstance(obj, (Sequence, Set)) and not isinstance(obj, string_types):
            iterator = enumerate
        if iterator:
            if id(obj) not in memo:
                memo.add(id(obj))
                for path_component, value in iterator(obj):
                    for result in self.objwalk(value, path + (path_component,), memo):
                        yield result
                memo.remove(id(obj))
        else:
            yield path, obj
