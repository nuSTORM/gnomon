import argparse
from array import array 
import ROOT
import Configuration

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Grab gnomon data from Couch and convert to ROOT file')
    
    parser.add_argument('--name', '-n', help='name for the simulation output DB', type=str, required=True)
    parser.add_argument('--type', '-t', help='event type', type=str, required=True) 
    parser.add_argument('--filename', '-f', help='root filename', type=str)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--runs', '-r', metavar='N', type=int, nargs='+',
                    help='runs to process')
    group.add_argument('--all', '-a', action='store_true',
                    help='process all runs')


    args = parser.parse_args()
    
    Configuration.name = args.name
    Configuration.run = args.run

    config = Configuration.CouchConfiguration()
    db = config.getCurrentDB()
    print config.getAllRunsInDB()
    

    map_fun = """
function(doc) {
  if (doc.type == '%s') {
    emit(doc.type, doc); 
}
}
""" % args.type
    
    
    file = None
    if args.filename:
        file = ROOT.TFile(args.filename, 'RECREATE')
    else:
        file = ROOT.TFile('gnomon_%s_%d_%s.root' % (args.NAME,  config.getRunNumber(), args.type), 'RECREATE')
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
        
            ROOT.gROOT.ProcessLine( my_struct_code )
            
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
                
            t.Branch(key, ROOT.AddressOf(my_struct, key), '%s/%s' % (key, code))

        for key in keys:
            setattr(my_struct, key, doc[key])
            #print '%s:%s, ' % (key, doc[key])
                
        t.Fill()
    
    t.Write()
    file.Close()
