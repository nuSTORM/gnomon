import tempfile
import os
import time
import couchdb

#server = 'http://gnomon:balls@tasd.fnal.gov:5984/'
server = 'http://gnomon:harry@gnomon.iriscouch.com/'
#server = 'http://gnomon:balls@heplnm071.pp.rl.ac.uk:5984/'
couch = couchdb.Server(server)

number_of_events = 1000

fresh = False

if fresh:
    try:
        couch.delete('root')
    except:
        pass

flags = '--log_level WARNING --logfileless'

for momentum in [100, 139, 195, 271, 379, 528, 737, 1028, 1434, 2000, 5000]:
    for pid in [-13, 13]:
        db_name = 'malcolm_%d_%d' % (momentum, pid)
        if fresh:
            try:
                couch.delete(db_name)
            except:
                pass
            
        for run in range(16,17):
            print momentum, pid, run
            filename = tempfile.mkstemp()[1]
            file = open(filename, 'w')
    
            script = """
source /home/tunnell/env/gnomon/bin/activate
export COUCHDB_URL=%(server_url)s
cd $VIRTUAL_ENV/src/gnomon
time python simulate.py --name %(db_name)s --vertex 2000 -2000 0 -p --momentum 0 0 %(momentum)d --events %(number_of_events)d --pid %(pid)d %(flags)s --run %(run)d
time python digitize.py --name %(db_name)s %(flags)s --run %(run)d
./couch_to_ntuple.py --name %(db_name)s -t mchit %(flags)s --run %(run)d
./couch_to_ntuple.py --name %(db_name)s -t digit %(flags)s --run %(run)d
""" % {'momentum': momentum, 'db_name' : db_name, 'number_of_events' : number_of_events, 'pid' : pid, 'run' : run, 'flags':flags, 'server_url':server}

            file.write(script)
            file.close()

            time.sleep(1)
            job_name = '%s_%s' % (db_name, run)
            os.system('qsub -N %s %s' % (job_name, filename))
