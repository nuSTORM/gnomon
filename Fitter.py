"""Fitter routines"""

import logging
import sys

from scipy import *
from matplotlib import *
from pylab import *
from scipy.optimize import leastsq

import Configuration

class VlenfPolynomialFitter():
    """The VLENF digitizer where the energy deposited is multiplied by a generic
    energy scale."""

    def __init__(self):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

        self.config = Configuration.DEFAULT()
        self.commit_threshold = self.config.getCommitThreshold()

        self.db = self.config.getCurrentDB()

        self.tracks = []

    def Fit(self, view):
        """Returns results of fit

        """
        z = view['z']
        trans = view['trans']
 
        def dbexpl(t,p):
            return(p[0] + p[1] * t**2)

        def residuals(p,data,t):
            err = data - dbexpl(t,p)
            return err
        
        p0 = [0.5,1] # initial guesses                                                             
        pbest = leastsq(residuals,p0,args=(trans, z),full_output=1)
        bestparams = pbest[0]
        cov_x = pbest[1]
        good_of_fit = sum(pbest[2]['fvec'] ** 2)                                                        
        #print 'best fit parameters ',bestparams                                                         
        #print cov_x
        datafit = dbexpl(z,bestparams)
        #plot(z,trans,'x',z,datafit,'r')
        #self.log.error('data %s %s', str(z), str(trans))
        #self.log.error('fit %s %s', str(z), str(datafit))
        #xlabel('Time')
        #title('Curve-fitting example')
        #grid(True)
        #show()

        doc = {}
        doc['params'] = list(bestparams)
        doc['z'] = list(z)
        doc['trans'] = list(trans)
        doc['datafit'] = list(datafit)
        doc['good_of_fit'] = good_of_fit
        return doc

    def Process(self):
        hits_dict = {}

        map_fun = """
function(doc) {
if (doc.type == 'digit' && doc.number_run == %d)
emit(doc.number_event, [doc.view, doc.position]);
 }""" % self.config.getRunNumber()


        last_event = None
        X_view = {'trans' : numpy.array([]), 'z' : numpy.array([])}
        Y_view = {'trans' : numpy.array([]), 'z' : numpy.array([])}
        for row in self.db.query(map_fun):
            event = row.key

            if last_event == None:
                last_event = event
            elif last_event != event:
                #self.log.error('X_view: %s', str(X_view))
                #self.log.error('Y_view: %s', str(Y_view))
                try:
                    for view in [X_view, Y_view]:
                        for key in view:
                            assert len(view[key]) > 10
                    doc = {}
                    doc['type'] = 'track'
                    doc['x'] = self.Fit(X_view)
                    doc['y'] = self.Fit(Y_view)
                    self.tracks.append(doc)
                    self.bulkCommit()
                except:
                    self.log.error('skipping!')

                X_view = {'trans' : numpy.array([]), 'z' : numpy.array([])}
                Y_view = {'trans' : numpy.array([]), 'z' : numpy.array([])}
                last_event = event


            view, position = row.value

            if view == 'X':
                X_view['trans'] = append(X_view['trans'], position['x'])
                X_view['z'] = append(X_view['z'], position['z'])
            else:
                Y_view['trans'] = append(Y_view['trans'], position['y'])
                Y_view['z'] = append(Y_view['z'], position['z'])
                

    def bulkCommit(self, force=False):
        self.log.info('Bulk commit of tracks requested')
        size = sys.getsizeof(self.tracks)
        self.log.debug('Size of tracks bulk commit in bytes: %d', size)
        if size > self.commit_threshold or force:
            self.log.info('Commiting %d bytes to CouchDB' % size)
            self.db.update(self.tracks)
            self.tracks = []
