import tempfile
import sys
import os
import shutil
import math
import random


servers = [
    #'http://gnomon:balls@nustorm.physics.ox.ac.uk:5984/',
    'http://gnomon:balls@tasd.fnal.gov:5984/'
]

polarity = '-'

number_of_events = 100000
repeat_point = 20  # how many times to redo same point

flags = '--log_level CRITICAL'

random.seed()

tempdir = tempfile.mkdtemp()

to_simulate = []
to_simulate.append(('flat', -14))
to_simulate.append(('flat', 14))
to_simulate.append(('flat', 12))

for db_settings in to_simulate:
    energy_dist, pid = db_settings
    #db_name = "_".join(map(str, db_settings))
    #db_name = '%s_fiducill' % db_name
    db_name = 'mm'

    for i in range(repeat_point):
        server = random.choice(servers)

        run = random.randint(1, sys.maxint)
        my_file = open(os.path.join(tempdir, '%s_%d' % (db_name, run)), 'w')

        this_number_evts = number_of_events #* 10**i

        script = """
source /home/tunnell/env/gnomon/bin/activate
cd $VIRTUAL_ENV/src/gnomon
source setup.sh
export COUCHDB_URL=%(server_url)s
time python bin/simulate.py --name %(db_name)s --pid %(pid)d --distribution %(energy)s --events %(this_number_evts)d %(flags)s --run %(run)d --polarity %(polarity)s
""" % {'db_name': db_name,
       'this_number_evts': this_number_evts,
       'run': run,
       'flags': flags,
       'server_url': server,
       'polarity': polarity,
       'energy': energy_dist,
       'pid': pid}

        my_file.write(script)
        my_file.close()

        print script

        job_name = '%s_%s' % (db_name, run)
        print 'filename', my_file.name

        hours = float(this_number_evts) / 1000.0
        hours = math.ceil(hours)
        extra_commands = '-l cput=%d:00:00' % hours
        #extra_commands = ''

        command = 'qsub %s -N %s %s' % (extra_commands, job_name, my_file.name)

        print command
        os.system(command)
        #time.sleep(1)

shutil.rmtree(tempdir)
