"""Fitter routines"""

import logging
import sys

from scipy import *
from matplotlib import *
from pylab import *
from scipy.optimize import leastsq

class VlenfPolynomialFitter():
    """The VLENF digitizer where the energy deposited is multiplied by a generic
    energy scale."""

    def __init__(self):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

        self.tracks = []

    def Shutdown(self):
        pass

    def Fit(self, view):
        """Returns results of fit

        """
        z = view['z']
        trans = view['trans']
 
        def dbexpl(t,p):
            if p[0] >= 0:
                return(p[0] + p[1] * t**2)
            else:
                return(p[0] - p[1] * t**2)

        def residuals(p,data,t):
            err = data - dbexpl(t,p)
            return err
        
        p0 = [0.5,1] # initial guesses                                                             
        pbest = leastsq(residuals,p0,args=(trans, z),full_output=1)
        bestparams = pbest[0]
        cov_x = pbest[1]
        good_of_fit = sum(pbest[2]['fvec'] ** 2)                                                        
        datafit = dbexpl(z,bestparams)

        doc = {}
        doc['params'] = list(bestparams)
        doc['z'] = list(z)
        doc['trans'] = list(trans)
        doc['gof'] = good_of_fit
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
        try:
            fitx_doc = self.Fit(X_view)
            fity_doc = self.Fit(Y_view)

            for fit_doc in [fitx_doc, fity_doc]:
                assert len(fit_doc['params']) == 2

            doc['gof_x'] = fitx_doc['gof']
            doc['gof_y'] = fity_doc['gof']

            doc['x0'] = fitx_doc['params'][0]
            doc['x1'] = fitx_doc['params'][1]
            
            doc['y0'] = fity_doc['params'][0]
            doc['y1'] = fity_doc['params'][1]
            
            doc['x'] = fitx_doc
            doc['y'] = fity_doc

            doc['analyzable'] = True
        except:
            doc['analyzable'] = False
            
        doc['short'] = short
        return [doc]
