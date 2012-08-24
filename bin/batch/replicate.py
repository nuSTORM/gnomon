import couchdb
import urlparse
import os


servers = ['http://gnomon:balls@tasd.fnal.gov:5984/',
           'http://gnomon:balls@nustorm.physics.ox.ac.uk:5984/']

master_url = servers[1]
master_couch = couchdb.Server(master_url)

slave_url = servers[0]
slave_couch = couchdb.Server(slave_url)

be_continuous = True

for dbname in master_couch:
    if dbname[0] != '_':
        slave_link = dbname  # urlparse.urljoin(slave_url, dbname)
        master_link = urlparse.urljoin(master_url, dbname)

        print dbname
        print '\tmaster:', master_link
        print '\tslave:', slave_link

        slave_couch.replicate(master_link, slave_link,
                              continuous=be_continuous, create_target=True)
