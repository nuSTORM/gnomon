"""Fitter routines"""

import logging
import sys

from scipy import *
from matplotlib import *
from pylab import *
from scipy.optimize import leastsq

#from pygraph.readwrite import markup
from pygraph.classes.digraph import digraph
from pygraph.algorithms import sorting
from Graph import Graph

bar_width = 10.0 # get from GDML!! BUG FIXME
layer_width = 40.0
width_threshold = 5*bar_width

class EmptyTrackFromDigits():
    """ Prepare for track extraction """

    def Shutdown(self):
        pass

    def Process(self, docs):
        run = None
        event = None
        
        new_docs = []

        tracks = {'x' : {}, 'y': {}}
        tracks['x']['LEFTOVERS'] = []
        tracks['y']['LEFTOVERS'] = []
        
        for doc in docs:
            if doc['type'] != 'digit':
                new_docs.append(doc)
                continue
            
            if event == None: event = doc['event']
            if run == None:   run   = doc['run']
            assert run == doc['run'] and event == doc['event']
            
            view, position = doc['view'], doc['position']
            
            if view == 'X':
                tracks['x']['LEFTOVERS'].append((position['z'], position['x']))
            else:
                tracks['y']['LEFTOVERS'].append((position['z'], position['y']))
                
        doc = {}
        doc['type'] = 'track'

        doc['run'] = run
        doc['event'] = event

        doc['analyzable'] = True
        doc['classification'] = {}
        doc['tracks'] = tracks

        new_docs.append(doc)

        return new_docs

class ExtractTracks():
    """Extract tracks with graph theoretic concepts"""

    def __init__(self):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)
    
    def Shutdown(self):
        pass
    
    def Process(self, docs):
        run = None
        event = None
        
        new_docs = []

        nodes = []
        
        for doc in docs:
            if doc['type'] != 'track':
                new_docs.append(doc)
                continue

            tracks = doc['tracks']
            doc['graph'] = {}

            previous = []
            for view in ['x', 'y']:
                self.log.info('Working on view %s' % view)
                points = tracks[view]['LEFTOVERS']

                #doc['graph']['gr1'] = markup.write(gr)

                dag = Graph()
                gr = dag.CreateVertices(points)
                gr = dag.CreateDirectedEdges(points, gr, layer_width)
                if gr.edges() == []:
                    continue

                parent_node = dag.FindParentNode(gr)
                gr1, length1, gr = dag.ComputeLongestPath(gr, parent_node)

                parent_node = dag.FindParentNode(gr)
                gr2, length2, gr = dag.ComputeLongestPath(gr, parent_node)

                if float(length1) == 0.0:
                    doc['analyzable'] = False

                tracks[view][length1] = gr1
                tracks[view][length2] = gr2
                tracks[view]['LEFTOVERS'] = gr.nodes()

                doc['classification']['%s_length1' % view] = length1
                doc['classification']['%s_length2' % view] = length2
                
            doc['tracks'] = tracks

            new_docs.append(doc)

        return new_docs

            
class VlenfPolynomialFitter():
    """The VLENF digitizer where the energy deposited is multiplied by a generic
    energy scale."""

    def __init__(self):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

        self.tracks = []

    def Shutdown(self):
        pass

    def Fit(self, zx):
        """Returns results of fit

        """

        z, trans = zip(*zx)

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
            if 'type' not in doc or doc['type'] != 'track' or doc['analyzable'] == False:
                new_docs.append(doc)
                continue

            tracks = doc['tracks']

            lx = doc['classification']['length_x']
            fitx_doc = self.Fit(tracks['x'][lx])
            ly = doc['classification']['length_y']
            fity_doc = self.Fit(tracks['y'][ly])

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
