import couchdb
import urlparse
import os

server = 'http://gnomon:balls@tasd.fnal.gov:5984'
couch = couchdb.Server(server)

for momentum in [100, 500, 1000, 2000]:
    for pid in [-13, 13]:
        db_name = 'malcolm_%d_%d' % (momentum, pid)
        try:
            couch.create(db_name)
        except:
            pass
        print """curl -X POST -d '{"create_target":true, "source":"http://gnomon:balls@127.0.0.1:5985/%s","target":"http://localhost:5984/%s"}'     http://gnomon:balls@tasd.fnal.gov:5984/_replicate -H "Content-Type: application/json" """ % (db_name, db_name)
