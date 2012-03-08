import couchdb
import urlparse
import os

for momentum in [100, 139, 195, 271, 379, 528, 737, 1028, 1434, 2000, 5000]:
    for pid in [-13, 13]:
        db_name = 'malcolm_%d_%d' % (momentum, pid)
        print db_name
