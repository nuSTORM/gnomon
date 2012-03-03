#!/usr/bin/env python 
import argparse
from array import array
import ROOT

import Configuration
import Logging

if __name__ == "__main__":
    my_description = 'Grab gnomon data from Couch and convert to ROOT file'
    parser = argparse.ArgumentParser(description=my_description)

    parser.add_argument('--name', '-n', help='DB in CouchDB for output',
                        type=str, required=True)
    parser.add_argument('--type', '-t', help='event type', type=str,
                        required=True)
    parser.add_argument('--filename', '-f', help='root filename', type=str)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--runs', '-r', metavar='N', type=int, nargs='+',
                    help='run(s) to process')
    group.add_argument('--all', '-a', action='store_true',
                    help='process all runs')

    Logging.addLogLevelOptionToArgs(parser)  #  adds --log_level 
    args = parser.parse_args()

    Logging.setupLogging(args.log_level)  # Console/file/stdout/stderr logs 

    Configuration.name = args.name
    # Configuration.run # not used

    config = Configuration.CouchConfiguration()
    db = config.getCurrentDB()

    if args.all:
        print 'using all runs'
        addition = ''
    else:
        print 'using runs', args.runs
        addition = 'if('
        run_conditions = ['doc.run == %d' % run for run in args.runs]
        print run_conditions
        print " || ".join(run_conditions)
        addition += " || ".join(run_conditions)
        addition += ')'

    map_fun = """
function(doc) {
  if (doc.type == '%s') {
    %s
    emit(doc.type, doc);
}
}
""" % (args.type, addition)

    print 'debug', map_fun

    file = None
    if args.filename:
        if '.root' not in args.filename:
            print 'error: no .root in filename!'
        file = ROOT.TFile(args.filename, 'RECREATE')
    else:
        file = ROOT.TFile('gnomon_%s_%s.root' % (args.name, args.type),
                          'RECREATE')
    t = ROOT.TTree('t', '')

    my_struct = None

    for row in db.query(map_fun):
        doc = dict(row.value)

        keys = [str(x) for x in doc.keys() if x[0] != '_']

        if my_struct == None:
            my_struct_code = 'struct MyStruct {'

            for key in keys:
                my_value = doc[key]
                my_type = type(my_value)

                if my_type == unicode:
                    my_struct_code += 'char %s[256];' % key
                elif my_type == int:
                    my_struct_code += 'int %s;' % key
                elif my_type == float:
                    my_struct_code += 'float %s;' % key
                else:
                    raise ValueError

            my_struct_code += '};'
            print my_struct_code

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
            else:
                raise ValueError

            t.Branch(key, ROOT.AddressOf(my_struct, key),
                     '%s/%s' % (key, code))

        for key in keys:
            setattr(my_struct, key, doc[key])

        t.Fill()

    t.Write()
    file.Close()
