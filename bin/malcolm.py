import tempfile
import os
import time
import couchdb

couch = couchdb.Server(os.getenv('COUCHDB_URL'))

number_of_events = 100

for momentum in [100, 139, 195, 271, 379, 528, 737, 1028, 1434, 2000, 5000]:
    for pid in [-13, 13]:
        for run in range(1,2):
            print momentum, pid, run
            filename = tempfile.mkstemp()[1]
            file = open(filename, 'w')
        
            db_name = 'malcolm_%d_%d' % (momentum, pid)
            try:
                couch.delete(db_name)
            except:
                pass
    
            script = """
source /home/tunnell/env/gnomon/bin/activate
cd $VIRTUAL_ENV/src/gnomon
time python simulate.py --name %(db_name)s --vertex 2000 -2000 0 -p --momentum 0 0 %(momentum)d --events %(number_of_events)d --pid %(pid)d --log_level INFO --run %(run)d
time python digitize.py --name %(db_name)s
./couch_to_ntuple.py --name %(db_name)s -a -t mchit
./couch_to_ntuple.py --name %(db_name)s -a -t digit
""" % {'momentum': momentum, 'db_name' : db_name, 'number_of_events' : number_of_events, 'pid' : pid, 'run' : run}

            print 'script:', script
            file.write(script)
            file.close()

            time.sleep(1)
            job_name = '%s_%s' % (db_name, run)
            os.system('qsub -N %s %s' % (job_name, filename))
