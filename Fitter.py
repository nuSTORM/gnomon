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

    def Shutdown(self):
        pass

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
        grid(True)
        show()

        doc = {}
        doc['params'] = list(bestparams)
        doc['z'] = list(z)
        doc['trans'] = list(trans)
        doc['datafit'] = list(datafit)
        doc['good_of_fit'] = good_of_fit
        return doc

    def Process(self, docs):
        X_view = {'trans' : numpy.array([]), 'z' : numpy.array([])}
        Y_view = {'trans' : numpy.array([]), 'z' : numpy.array([])}

        for doc in docs:
            view, position = doc['view'], doc['position']

            if view == 'X':
                X_view['trans'] = append(X_view['trans'], position['x'])
                X_view['z'] = append(X_view['z'], position['z'])
            else:
                Y_view['trans'] = append(Y_view['trans'], position['y'])
                Y_view['z'] = append(Y_view['z'], position['z'])
                

        short = False
        for view in [X_view, Y_view]:
            for key in view:
                if len(view[key]) < 10:
                    short = True
        doc = {}
        doc['type'] = 'track'
        doc['x'] = self.Fit(X_view)
        doc['y'] = self.Fit(Y_view)
        doc['short'] = short
        return [doc]
