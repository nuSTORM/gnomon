import couchdb
import urlparse
import os

remote_url = os.getenv('COUCHDB_URL')
remote_couch = couchdb.Server(remote_url)

local_url = 'http://gnomon:balls@127.0.0.1:5984'
local_couch =couchdb.Server(local_url)

for momentum in [100, 139, 195, 271, 379, 528, 737, 1028, 1434, 2000]:
    for pid in [-13, 13]:
        print 'remote', remote_url
        print 'local', local_url
        
        db_name = 'malcolm_%d_%d' % (momentum, pid)
        local_link = urlparse.urljoin(local_url, db_name)
        
        dest_link =  urlparse.urljoin(remote_url, db_name)

        print local_link, dest_link

        local_couch.replicate(dest_link, local_link, continous=True, create_target=True)
            
