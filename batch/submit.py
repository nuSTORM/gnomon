import tempfile
import os
import time
import couchdb

import batch_queue_config

#server = 'http://gnomon:balls@tasd.fnal.gov:5984/'
server = 'http://gnomon:harry@gnomon.iriscouch.com/'
#server = 'http://gnomon:balls@172.16.84.2:8080/'
#server = 'http://gnomon:balls@heplnm071.pp.rl.ac.uk:5984/'
couch = couchdb.Server(server)

number_of_events = 10000

flags = '--log_level WARNING --logfileless'

for momentum in batch_queue_config.momenta:
    for pid in batch_queue_config.pids:
        for polarity in ['-', '+']:
            if polarity == '-':
                db_name = 'malcolm_minus_%d_%d' % (momentum, pid)
            else:
                db_name = 'malcolm_plus_%d_%d' % (momentum, pid)
                
            for run in range(1, 2):
                print momentum, pid, run
                filename = tempfile.mkstemp()[1]
                file = open(filename, 'w')

                sleep_time = run - 1
    
                script = """
source /home/tunnell/env/gnomon/bin/activate
export COUCHDB_URL=%(server_url)s
cd $VIRTUAL_ENV/src/gnomon
time python simulate.py --name %(db_name)s --vertex 2000 -2000 0 -p --momentum 0 0 %(momentum)d --events %(number_of_events)d --pid %(pid)d %(flags)s --run %(run)d --polarity %(polarity)s
sleep 5m
time python digitize.py --name %(db_name)s %(flags)s --run %(run)d
sleep 5m
#./couch_to_ntuple.py --name %(db_name)s -t mchit %(flags)s --run %(run)d
#./couch_to_ntuple.py --name %(db_name)s -t digit %(flags)s --run %(run)d
./fit.py --name %(db_name)s %(flags)s --run %(run)d
""" % {'momentum': momentum, 'db_name' : db_name, 'number_of_events' : number_of_events, 'pid' : pid, 'run' : run, 'flags':flags, 'server_url':server, 'polarity' : polarity}
                
                file.write(script)
                file.close()

                print script
                time.sleep(10)
                job_name = '%s_%s' % (db_name, run)
                os.system('qsub -N %s %s' % (job_name, filename))
