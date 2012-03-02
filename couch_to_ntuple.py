import argparse
from array import array 
import ROOT
import Configuration

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Grab gnomon data and Ntuple')
    
    parser.add_argument('NAME', help='name for the simulation output', type=str)
    parser.add_argument('TYPE', help='event type', type=str) 
    parser.add_argument('--filename', help='root filename', type=str)

    args = parser.parse_args()
    
    Configuration.name = args.NAME
    Configuration.run = 0

    config = Configuration.CouchConfiguration()
    db = config.getCurrentDB()

    map_fun = """
function(doc) {
  if (doc.type == '%s') {
    emit(doc.type, doc); 
}
}
""" % args.TYPE
    
    file = None
    if args.filename:
        file = ROOT.TFile(args.filename, 'RECREATE')
    else:
        file = ROOT.TFile('gnomon_%s_%d_%s.root' % (args.NAME,  config.getRunNumber(), args.TYPE), 'RECREATE')
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
                
            t.Branch(key, ROOT.AddressOf(my_struct, key), '%s/%s' % (key, code))

        for key in keys:
            setattr(my_struct, key, doc[key])
            #print '%s:%s, ' % (key, doc[key])
                
        t.Fill()
    
    t.Write()
    file.Close()
