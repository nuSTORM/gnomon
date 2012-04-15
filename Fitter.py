"""Fitter routines"""

import logging
import sys

from scipy import *
from matplotlib import *
from pylab import *
from scipy.optimize import leastsq

class ExtractTrack():
    """Extract track"""

    def __init__(self):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

        self.bar_width = 10.0 # get from GDML!! BUG FIXME

    def ExtractFromView(self, z, x):
        #  Create a lookup table
        point_dict = {}
        for z0, x0 in zip(z,x):
            if z0 not in point_dict:
                point_dict[z0] = []
            point_dict[z0].append(x0)

        #  Grab points in 'z' with hits, and reverse sort
        keys = point_dict.keys()
        keys.sort()
        keys.reverse()

        if len(keys) == 0:
            return [], [], 0.0

        length = 0.0
        new_z, new_x = [ keys[0] ], [ point_dict[keys[0]][0] ]
        for z1 in keys:
            z0 = new_z[-1]
            x0 = new_x[-1]
            best_x = None

            for x1 in point_dict[z1]:
                if best_x == None:
                    best_x = x1

                dz = z1 - z0
                dx = x1 - x0

                if math.hypot(dz, dx) < math.hypot(z1 - z0, best_x - x0):
                    best_x = x1

            if math.hypot(z1 - z0, best_x - x0) > 100.0:  # threshold, BUG FIXME, GDML

                return new_z, new_x, length

            length += math.hypot(z1 - z0, best_x - x0)
            new_z.append(z1)
            new_x.append(best_x)

            # Determine if there are neighbors (ie. doublets)
            for x_other in point_dict[z1]:
                if math.fabs(x_other - best_x) == self.bar_width:
                    new_z.append(z1)
                    new_x.append(x_other)

        return new_z, new_x, length

    def Process(self, docs):
        run = None
        event = None

        new_docs = []

        X_view = {'trans' : [], 'z' : [], 'E' : []}
        Y_view = {'trans' : [], 'z' : [], 'E': [] }

        for doc in docs:
            if doc['type'] != 'digit':
                new_docs.append(doc)
                continue

            if event == None: event = doc['event']
            if run == None:   run   = doc['run']
            assert run == doc['run'] and event == doc['event']

            view, position = doc['view'], doc['position']

            if view == 'X':
                X_view['trans'].append(position['x'])
                X_view['z'].append(position['z'])
                X_view['E'].append(doc['counts_adc'])
            else:
                Y_view['trans'].append(position['y'])
                Y_view['z'].append(position['z'])
                Y_view['E'].append(doc['counts_adc'])


        doc = {}
        doc['type'] = 'track'
        doc['run'] = run
        doc['event'] = event
        doc['x'] = X_view
        doc['y'] = Y_view

        doc['classification'] = {}

        z, trans, l = self.ExtractFromView(X_view['z'], X_view['trans'])

        doc['classification']['length_x']   = l
        doc['extracted_x'] = {'z' : z, 'trans' : trans, 'E': X_view['E']}

        z, trans, l = self.ExtractFromView(Y_view['z'], Y_view['trans'])

        doc['classification']['length_y']   = l
        doc['extracted_y'] = {'z' : z, 'trans' : trans, 'E': Y_view['E']}

        new_docs.append(doc)
        return new_docs

    def Shutdown(self):
        pass

class VlenfPolynomialFitter():
    """The VLENF digitizer where the energy deposited is multiplied by a generic
    energy scale."""

    def __init__(self):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

        self.tracks = []

    def Shutdown(self):
        pass

    def Fit(self, z, trans):
        """Returns results of fit

        """

        assert len(trans) == len(z)
        ndf = len(z) - 3
        
        z = np.array(z)
        trans = np.array(trans)

        def dbexpl(t,p):
            if p[0] >= 0:
                return(p[0] - p[1] * t + p[2] * t**2)
            else:
                return(p[0] - p[1] * t - p[2] * t**2)

        def residuals(p,data,t):
            err = data - dbexpl(t,p)
            return err

        doc = {}

        try:
            assert ndf > 0

            p0 = [1,0,0] # initial guesses
            pbest = leastsq(residuals,p0,args=(trans, z),full_output=1)
            bestparams = pbest[0]
            cov_x = pbest[1]
            good_of_fit = sum(pbest[2]['fvec'] ** 2)
            good_of_fit = float(good_of_fit / ndf)
            datafit = dbexpl(z,bestparams)
            doc['params'] = list(bestparams)
            doc['gof'] = good_of_fit
        except:
            doc['gof'] = 'FAIL'
            doc['params'] = [0,0,0]

        return doc

    def Process(self, docs):
        new_docs = []
        for doc in docs:
            if 'type' not in doc or doc['type'] != 'track':
                new_docs.append(doc)
                continue

            fitx_doc = self.Fit(doc['extracted_x']['z'], doc['extracted_x']['trans'])
            fity_doc = self.Fit(doc['extracted_y']['z'], doc['extracted_y']['trans'])

            for fit_doc in [fitx_doc, fity_doc]:
                assert len(fit_doc['params']) == 3

            doc['gof_x'] = fitx_doc['gof']
            doc['gof_y'] = fity_doc['gof']

            if doc['gof_x'] == 'FAIL' or doc['gof_y'] == 'FAIL':
                doc['analyzable'] = False
            else:
                doc['analyzable'] = True

            doc['x0'] = fitx_doc['params'][0]
            doc['x1'] = fitx_doc['params'][1]
            doc['x2'] = fitx_doc['params'][2]

            doc['y0'] = fity_doc['params'][0]
            doc['y1'] = fity_doc['params'][1]
            doc['y2'] = fity_doc['params'][2]


            new_docs.append(doc)
        return new_docs
