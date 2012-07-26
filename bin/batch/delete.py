"""Delete everything"""
import argparse
import couchdb


def run():
    server_list = ['http://gnomon:balls@tasd.fnal.gov:5984/']

    for server in server_list:
        server = couchdb.Server(server)

        for dbname in server:
            if dbname[0] != '_':
                server.delete(dbname)

if __name__ == "__main__":
    run()
