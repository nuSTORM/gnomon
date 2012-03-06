import couchdb
import urlparse
import os

base_url = os.getenv('COUCHDB_URL')
couch = couchdb.Server(base_url)
base_url2 = os.getenv('COUCHDB_URL2')
couch2 =couchdb.Server(base_url2)

for momentum in [100, 139, 195, 271, 379, 528, 737, 1028, 1434, 2000]:
    for pid in [-13, 13]:
            db_name = 'malcolm_%d_%d' % (momentum, pid)
            local_url = urlparse.urljoin(base_url, db_name)

            dest_url =  urlparse.urljoin(base_url2, db_name)

            print local_url, dest_url

            try:
                pass#couch2.create(db_name)
            except:
                pass

            couch.replicate(local_url, dest_url, continous=True)
            
