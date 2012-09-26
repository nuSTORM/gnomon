import tempfile
import sys
import os
import time
import couchdb
import shutil
import math
import random
import batch_queue_config

server = 'http://gnomon:balls@tasd.fnal.gov:5984/'

number_of_events = 100000
repeat_point = 1  # how many times to redo same point

flags = '--log_level WARNING'

random.seed()

tempdir = tempfile.mkdtemp()

energy = 10000.0  # GeV

for pid in [211, -211]:
    polarity = '0'

    for i in range(repeat_point):
        server = 'http://gnomon:balls@tasd.fnal.gov:5984/'

        file = open(os.path.join(tempdir, 'distance_%d' % (i)), 'w')

        run = random.randint(1, sys.maxint)  # helps qsub know which run it is

        script = """
source /home/tunnell/env/gnomon/bin/activate
export COUCHDB_URL=%(server_url)s
cd $VIRTUAL_ENV/src/gnomon
time python simulate.py --name distance --vertex 0 0 0 --events %(number_of_events)d %(flags)s --run %(run)d --polarity 0 --energy %(energy)f --pid %(pid)d
""" % {'number_of_events': number_of_events, 'run': run, 'flags': flags, 'server_url': server, 'energy': energy,
       'pid': pid}

        file.write(script)
        file.close()

        print script

        job_name = 'distance_%s' % (run)
        print 'filename', file.name

        hours = float(number_of_events) / 1000.0
        hours = math.ceil(hours)
        #extra_commands = '-l cput=%d:00:00' % hours
        extra_commands = ''

        command = 'qsub %s -N %s %s' % (extra_commands, job_name, file.name)

        print command
        #os.system(command)
        time.sleep(1)

shutil.rmtree(tempdir)
