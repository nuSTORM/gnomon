import tempfile
import sys
import os
import time
import couchdb
import shutil
import math
import random
import batch_queue_config

servers = ['http://gnomon:balls@tasd.fnal.gov:5984/',
           'http://gnomon:harry@gnomon.iriscouch.com/',
           'http://gnomon:balls@172.16.84.2:8080/']

number_of_events = 100
repeat_point = 1 # how many times to redo same point

flags = '--log_level WARNING --logfileless'

random.seed()

tempdir = tempfile.mkdtemp()

for db_name in ['mu_sig', 'mu_bar_bkg']:
    polarity = '-'

    for i in range(repeat_point):
        server = 'http://gnomon:balls@tasd.fnal.gov:5984/'
        #server = 'http://gnomon:balls@172.16.84.2:8080/'

        couch = couchdb.Server(server)
        file = open(os.path.join(tempdir, '%s_%d' % (db_name, i)), 'w')

        run = random.randint(1, sys.maxint)

        script = """
source /home/tunnell/env/gnomon/bin/activate
export COUCHDB_URL=%(server_url)s
cd $VIRTUAL_ENV/src/gnomon
time python simulate.py --name %(db_name)s2 --vertex 1000 -1000 0 -g %(db_name)s --events %(number_of_events)d %(flags)s --run %(run)d --polarity %(polarity)s
""" % {'db_name' : db_name, 'number_of_events' : number_of_events, 'run' : run, 'flags':flags, 'server_url':server, 'polarity' : polarity}
                
        file.write(script)
        file.close()
                
        print script
                
        job_name = '%s_%s' % (db_name, run)
        print 'filename', file.name

        hours = float(number_of_events) / 1000.0
        hours = math.ceil(hours)
        extra_commands = '-l cput=%d:00:00' % hours

        command = 'qsub %s -N %s %s' % (extra_commands, job_name, file.name)

        print command
        os.system(command)
        time.sleep(1)


shutil.rmtree(tempdir)

