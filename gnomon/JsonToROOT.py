"""Create a ROOT file from a Schema and JSON output"""

import ROOT
from collections import Mapping, Set, Sequence
import validictory

class JsonToRootConverter(object):
    """Convert JSON output to a ROOT file

    Start with a JSON schema which maps keys to their type and also where in the ROOT
    file they should go.  Then get passed each event.  There are two main initialization
    events: a struct is created in memory using ROOT and CINT, then a TTree is bound to
    the branches within the struct."""

    def __init__(self, schema):
        self.schema = schema

        #  Create ROOT file and TTree
        filename = 'gnomon.root'
        self.file = ROOT.TFile(filename, 'RECREATE')
        self.t = ROOT.TTree('t', '')

         # This code will be passed into CINT
        self.names_lookup, self.types_lookup = self.make_lookups(schema)
        my_struct_code = self.form_cint(self.names_lookup, self.types_lookup)

        print 'Using following structure for converting Python: %s' %  my_struct_code
        print 'name lookup', self.names_lookup

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
            elif my_type == 'number':
                code = 'F'
            elif my_type == 'object':
                pass
            elif my_type == 'boolean':
                code = 'O'
            else:
                raise ValueError

            x = ROOT.AddressOf(self.my_struct, str(name))

            self.t.Branch(name, x,  '%s/%s' % (name, code))

    def Process(self, doc):
        try:
            validictory.validate(doc, self.schema, required_by_default=False)
        except ValueError, error:
            print error
            raise
        
        for key, val in self.objwalk(doc):
            trunc_key = key  # trunacte off end 
            if len(trunc_key) > 1 and trunc_key[0] == 'mc':
                continue
            #print trunc_key, self.names_lookup.keys()
            if trunc_key in self.names_lookup.keys():
                setattr(self.my_struct,
                        self.names_lookup[trunc_key],
                        val)
                self.t.Fill()
                print 'fill', val, self.names_lookup[trunc_key]

    def Shutdown(self):
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

            print trunc_key
            if key[-1] == 'description':
                names_lookup[trunc_key] = val
                print 'hi'
            elif key[-1] == 'type':
                print 'bye'
                types_lookup[trunc_key] = val
            else:
                pass

        print 'TEST', names_lookup

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
