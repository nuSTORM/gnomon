import couchdb
import urlparse
import os

import batch_queue_config

server = 'http://gnomon:balls@tasd.fnal.gov:5984'
couch = couchdb.Server(server)

for momentum in batch_queue_config.momenta:
    for pid in batch_queue_config.pids:
        db_name = 'malcolm_%d_%d' % (momentum, pid)

        print db_name
