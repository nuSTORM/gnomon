"""Create a ROOT file from a Schema and JSON output"""

import ROOT


class JsonToRootConverter(object):
    def __init__(self, schema):
        filename = 'gnomon.root'
        file = ROOT.TFile(filename, 'RECREATE')
        t = ROOT.TTree('t', '')
        my_struct = None

        my_struct_code = 'struct MyStruct {'

        for key in schema['properties'].keys():
            print key

            my_value = doc[key]
            my_type = type(my_value)

            log.debug('C++ing %s %s', key, my_value)

            if my_type == unicode:
                my_struct_code += 'char %s[256];' % key
            elif my_type == int:
                my_struct_code += 'int %s;' % key
            elif my_type == float:
                my_struct_code += 'float %s;' % key
            elif my_type == dict:
                log.debug('Type check: Seeing if dict type is 3-vector')
                for element in elements_3vector:
                    if element not in my_value.keys():
                        raise ValueError('Dictionary is not 3-vector since missing %s',
                            element)
                    my_struct_code += 'float %s_%s;' % (key, element)
            else:
                raise ValueError('Unsupported type in JSON')

        my_struct_code += '};'
        log.info('Using following structure for converting Python: %s',
            my_struct_code)

        ROOT.gROOT.ProcessLine(my_struct_code)

        from ROOT import MyStruct

        my_struct = MyStruct()

        for key in keys:
            my_value = doc[key]
            my_type = type(my_value)

            code = None
            if my_type == unicode:
                code = 'C'
            elif my_type == int:
                code = 'I'
            elif my_type == float:
                code = 'F'
            elif my_type == dict:
                # Special case, need three branches
                code = 'F'
                for element in elements_3vector:
                    new_key = '%s_%s' % (key, element)
                    t.Branch(new_key, ROOT.AddressOf(my_struct, new_key),
                        '%s/%s' % (new_key, code))
                continue
            else:
                raise ValueError

            t.Branch(key, ROOT.AddressOf(my_struct, key),
                '%s/%s' % (key, code))

