import os
import couchdb
import logging
import Configuration
import sys
import pickle

class Manager:
    def __init__(self):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

        self.config = Configuration.GLOBAL_CONFIG
        assert self.config

    def Save(self, doc):
        raise NotImplementedError

    def Shutdown(self):
        pass

    def Process(self, docs):
        for doc in docs:
            self.Save(doc)


class CouchManager(Manager):
    def __init__(self):
        Manager.__init__(self)

        self.server_url = self.config['couchdb']['url']

        if os.getenv('COUCHDB_URL'):
            value = os.getenv('COUCHDB_URL')
            self.log.info('Environmental variable COUCHDB_URL: %s' % value)
            self.server_url = value

        self.server = couchdb.Server(self.server_url)
        self.server.version()
        
        self.db = self.setupDB(self.server, self.config['name'])
        self.commit_threshold = self.config['couchdb']['commit_threshold']
        self.docs = []

    def setupDB(self, couch, dbname):
        # Avoid race condition of two creating db
        db = None
        if dbname not in couch:
            self.log.info("DB doesn't exist so creating DB: %s", dbname)
            try:
                db = couch.create(dbname)
            except:
                self.log.error("Race condition caught")
                
            try:
                auth_doc = {}
                auth_doc['_id'] = '_design/auth'
                auth_doc['language'] = 'javascript'
                
                auth_doc['validate_doc_update'] = """
                function(newDoc, oldDoc, userCtx) {
                if (userCtx.roles.indexOf('_admin') !== -1) {
                return;
                } else {
                throw({forbidden: 'Only admins may edit the database'});
                }
                }
                """
                  
                db.save(auth_doc)
            except:
                self.log.error('Could not set permissions of %s' % dbname)

        else:
            db = couch[dbname]

        return db
                
    def Commit(self, force=False):
        self.log.debug('Bulk commit requested')
        size = sys.getsizeof(self.docs)

        self.log.debug('Size of docs in KB: %d', size)
        if size > self.commit_threshold or force:
            self.log.info('Commiting %d KB to CouchDB' % size)
            self.db.update(self.docs)
            self.docs = []

    def Save(self, doc):
        self.log.debug('Save()')
        self.docs.append(doc)
        self.Commit()

    def Shutdown(self):
        self.log.debug('Shutdown()')
        self.Commit(force=True)


class FileManager(Manager):
    def __init__(self):
        Manager.__init__(self)
        self.dir = '/data/mice/gnomon/'
        self.file_name = None

        self.file_path = None
        self.file = None

        self.file_path_lock = None

    def Open(self, type):
        try: os.mkdir(self.dir)
        except OSError: pass # already exists

        self.file_name = '%s_%s_%d' % (type, Configuration.name, Configuration.run)

        self.file_path = os.path.join(self.dir, self.file_name)
        self.file_path_lock = os.path.join(self.dir, '%s.lock' % self.file_name)

        if os.path.exists(self.file_path):
            raise ValueError('File exists!')

        if os.path.exists(self.file_path_lock):
            raise ValueError('Lock file exists!')

        self.file = open(self.file_path, 'w')

        # Create lock file
        file_lock = open(self.file_path_lock, 'w')
        file_lock.close()

    def Save(self, doc):
        assert isinstance(doc, dict)
        if self.file == None:
            self.Open(doc['type'])
        pickle.dump(doc, self.file)

    def Shutdown(self):
        self.file.close()

        #self.SendToCouch(self.file_path_tmp)

        os.remove(self.file_path_lock)
        #shutil.move(self.file_path_tmp, self.file_path_failed)
        #    raise

    def __del__(self):
        pass


def SendToCouch(filename):
    dir = '/data/mice/gnomon/'

    Configuration.run = int(filename.split('_')[-1])
    Configuration.name = '_'.join(filename.split('_')[1:-1])

    filepath = os.path.join(dir, filename)
    file = open(filepath, 'r')

    couch_dm = CouchManager()

    while 1:
        try:
            couch_dm.Save(pickle.load(file))
        except (EOFError, pickle.UnpicklingError):
            break

    couch_dm.Shutdown()


if __name__ == "__main__":
    dir = '/data/mice/gnomon/'

    for filename in os.listdir(dir):
        if filename.endswith('.lock'):
            continue

        lock_path = os.path.join(dir, '%s.lock' % filename)
        if os.path.exists(lock_path):
            continue


        SendToCouch(filename)
        os.remove(filename)
