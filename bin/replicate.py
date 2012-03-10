import couchdb
import urlparse
import os

remote_url = 'http://gnomon:balls@tasd.fnal.gov:5984/'
#remote_url = 'http://gnomon:balls@heplnm071.pp.rl.ac.uk:5984/'
remote_couch = couchdb.Server(remote_url)

local_url = 'http://gnomon:harry@gnomon.iriscouch.com/'
local_couch =couchdb.Server(local_url)

for momentum in [100, 139, 195, 271, 379, 528, 737, 1028, 1434, 2000]:
    for pid in [-13, 13]:
        db_name = 'malcolm_%d_%d' % (momentum, pid)
        print db_name

        print 'remote', remote_url
        print 'local', local_url
        
        local_link = urlparse.urljoin(local_url, db_name)
        
        dest_link =  urlparse.urljoin(remote_url, db_name)

        print local_link, dest_link

        local_couch.replicate(dest_link, local_link, continous=True, create_target=True)
        break
    break
            
