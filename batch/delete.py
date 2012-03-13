"""Delete everything but the ROOT output"""

import couchdb
import batch_queue_config

server_list = ['http://gnomon:balls@tasd.fnal.gov:5984/',
               'http://gnomon:harry@gnomon.iriscouch.com/',
               'http://gnomon:balls@172.16.84.2:8080/',]

for server in server_list:
    couch = couchdb.Server(server)

    # NEVER DELETE ROOT!

    for momentum in batch_queue_config.momenta:
        for pid in batch_queue_config.pids:
            for polarity in ['-', '+']:
                if polarity == '-':
                    db_name = 'malcolm_minus_%d_%d' % (momentum, pid)
                else:
                    db_name = 'malcolm_plus_%d_%d' % (momentum, pid)
                try:
                    couch.delete(db_name)
                except:
                    pass
