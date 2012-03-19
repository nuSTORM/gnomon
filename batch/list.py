import couchdb
import urlparse
import os

import batch_queue_config

server = 'http://gnomon:balls@tasd.fnal.gov:5984'
couch = couchdb.Server(server)

for momentum in batch_queue_config.momenta:
    for pid in batch_queue_config.pids:
        for polarity in ['-', '+']:
            if polarity == '-':
                db_name = 'malcolm_minus_%d_%d' % (momentum, pid)
            else:
                db_name = 'malcolm_plus_%d_%d' % (momentum, pid)

        print db_name
