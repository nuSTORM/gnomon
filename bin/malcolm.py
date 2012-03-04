import tempfile
import os
import time
import couchdb

couch = couchdb.Server(os.getenv('COUCHDB_URL'))

number_of_events = 1000

for momentum in [100, 139, 195, 271, 379, 528, 737, 1028, 1434, 2000]:
    for pid in [-13, 13]:
        print momentum, pid
        filename = tempfile.mkstemp()[1]
        print filename
        file = open(filename, 'w')
        
        db_name = 'malcolm_%d_%d' % (momentum, pid)
        try:
            couch.delete(db_name)
        except:
            pass
    
        script = """
source /home/tunnell/env/gnomon/bin/activate
cd $VIRTUAL_ENV/src/gnomon
time python simulate.py --name %(db_name)s --vertex 0 2000 0 -p --momentum 0 0 %(momentum)d --events %(number_of_events)d --logfileless --pid %(pid)d
""" % {'momentum': momentum, 'db_name' : db_name, 'number_of_events' : number_of_events, 'pid' : pid}

        print script
        file.write(script)
        file.close()

        time.sleep(1)
        os.system('qsub -N %s %s' % (db_name, filename))
