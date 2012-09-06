import tempfile
import sys
import os
import time
import shutil
import math
import random


servers = ['http://gnomon:balls@nustorm.physics.ox.ac.uk:5984/',
           'http://gnomon:balls@tasd.fnal.gov:5984/'
           ]

polarity = '-'

number_of_events = 1000
repeat_point = 2  # how many times to redo same point

flags = '--log_level INFO'

random.seed()

tempdir = tempfile.mkdtemp()

to_simulate = []
to_simulate.append(('muon', -14))
to_simulate.append(('electron', 14))
to_simulate.append(('electron', 12))

for db_settings in to_simulate:
    energy_dist, pid = db_settings
    db_name = "_".join(map(str, db_settings))
    #db_name = '%s_fiducia' % db_name

    for i in range(repeat_point):
        server = random.choice(servers)

        file = open(os.path.join(tempdir, '%s_%d' % (db_name, i)), 'w')

        run = random.randint(1, sys.maxint)

        this_number_evts = number_of_events * 10**i

        script = """
source /home/tunnell/env/gnomon/bin/activate
cd $VIRTUAL_ENV/src/gnomon
source setup.sh
export COUCHDB_URL=%(server_url)s
time python bin/simulate.py --name %(db_name)s --pid %(pid)d --distribution %(energy)s --events %(this_number_evts)d %(flags)s --run %(run)d --polarity %(polarity)s
""" % {'db_name': db_name, 'this_number_evts': this_number_evts, 'run': run, 'flags': flags, 'server_url': server, 'polarity': polarity, 'energy': energy_dist, 'pid': pid}

        file.write(script)
        file.close()

        print script

        job_name = '%s_%s' % (db_name, run)
        print 'filename', file.name

        hours = float(this_number_evts) / 1000.0
        hours = math.ceil(hours)
        extra_commands = '-l cput=%d:00:00' % hours
        #extra_commands = ''

        command = 'qsub %s -N %s %s' % (extra_commands, job_name, file.name)

        print command
        os.system(command)
        #time.sleep(1)


shutil.rmtree(tempdir)
