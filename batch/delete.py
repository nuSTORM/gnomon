"""Delete everything but the ROOT output"""
import argparse
import couchdb


def run(all, mchits, digits, tracks):
    server_list = ['http://gnomon:balls@tasd.fnal.gov:5984/']
    
    for server in server_list:
        server = couchdb.Server(server)

        for dbname in server:
            if dbname[0] != '_':
                if all:
                    server.delete(dbname)
                else:
                    db = server[dbname]
                    print db
                    map_fun = """
                    function(doc) {
                    if (doc.type == 'digit')
                    emit(null, 1)
                    }"""
                    
                    for row in db.query(map_fun, include_docs=True):
                        print row.doc
                
                
                    db.compact()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='delete couch info')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', '-a', action='store_true', help='all')
    group2 = group.add_mutually_exclusive_group()
    group2.add_argument('--mchits', '-m', action='store_true', help='mchits')
    group2.add_argument('--digits', '-d', action='store_true', help='digits')
    group2.add_argument('--tracks', '-t', action='store_true', help='tracks')

    args = parser.parse_args()
    run(args.all, args.mchits, args.digits, args.tracks)
