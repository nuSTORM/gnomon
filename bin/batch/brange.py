import tempfile
import sys
import os
import time
import shutil
import math
import random


servers = ['http://gnomon:balls@nustorm.physics.ox.ac.uk:5984/',
           'http://gnomon:balls@tasd.fnal.gov:5984/']

polarity = '-'

number_of_events = 1e6
repeat_point = 4  # how many times to redo same point

flags = '--log_level CRITICAL'

random.seed()

tempdir = tempfile.mkdtemp()

for material in ['iron_scint_bars', 'iron', 'scint']:
    for i in range(repeat_point):
        server = random.choice(servers)

        db_name = material

        file = open(os.path.join(tempdir, '%s_%d' % (db_name, i)), 'w')

        script = """
source /home/tunnell/env/gnomon/bin/activate
cd $VIRTUAL_ENV/src/gnomon
source setup.sh
export COUCHDB_URL=%(server_url)s
time python bin/range.py %(material)s""" % {'server_url': server, 'material': material}

        file.write(script)
        file.close()

        print script

        job_name = '%s' % (db_name)
        print 'filename', file.name

        hours = 2
        #extra_commands = '-l cput=%d:00:00' % hours
        extra_commands = ''

        command = 'qsub %s -N %s %s' % (extra_commands, job_name, file.name)

        print command
        os.system(command)
        time.sleep(1)


shutil.rmtree(tempdir)
