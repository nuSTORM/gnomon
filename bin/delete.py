"""Delete everything but the ROOT output"""

import couchdb

server_list = ['http://gnomon:balls@tasd.fnal.gov:5984/',
               'http://gnomon:harry@gnomon.iriscouch.com/',
               'http://gnomon:balls@172.16.84.2:8080/',]
for server in server_list:
    couch = couchdb.Server(server)
    
    for momentum in [100, 139, 195, 271, 379, 528, 737, 1028, 1434, 2000, 5000]:
        for pid in [-13, 13]:
            db_name = 'malcolm_%d_%d' % (momentum, pid)
            try:
                couch.delete(db_name)
            except:
                pass
