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

be_continous=False

for db_name in ['mu_bar_bkg2', 'mu_sig2']:
    local_link = urlparse.urljoin(local_url, db_name)
    dest_link =  urlparse.urljoin(remote_url, db_name)
    print local_link, '<-', dest_link
    local_couch.replicate(dest_link, local_link, continous=be_continous, create_target=True)

            
