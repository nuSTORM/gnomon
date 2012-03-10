import couchdb
import urlparse
import os


#remote_url = 'http://gnomon:harry@gnomon.iriscouch.com/' 
remote_url = 'http://gnomon:balls@tasd.fnal.gov:5984/'
#remote_url = 'http://gnomon:balls@heplnm071.pp.rl.ac.uk:5984/'
remote_couch = couchdb.Server(remote_url)

#local_url = 'http://gnomon:harry@gnomon.iriscouch.com/'
local_url = 'http://gnomon:balls@172.16.84.2:8080/'
local_couch =couchdb.Server(local_url)

be_continous=True

for momentum in [100, 139, 195, 271, 379, 528, 737, 1028, 1434, 2000]:
    for pid in [-13, 13]:
        db_name = 'malcolm_%d_%d' % (momentum, pid)

        local_link = urlparse.urljoin(local_url, db_name)
        dest_link =  urlparse.urljoin(remote_url, db_name)
        print local_link, '->', dest_link
        local_couch.replicate(local_link, dest_link, continous=be_continous, create_target=True)

local_link = urlparse.urljoin(local_url, db_name)
dest_link =  urlparse.urljoin(remote_url, db_name)
local_couch.replicate(local_link, dest_link, continous=be_continous, create_target=True)
            
