"""Fitter routines"""

import logging
import sys

from scipy import *
from matplotlib import *
from pylab import *
from scipy.optimize import leastsq

from pygraph.readwrite import markup
from pygraph.classes.digraph import digraph
from pygraph.algorithms import sorting
from Graph import Graph

bar_width = 10.0 # get from GDML!! BUG FIXME
layer_width = 40.0
width_threshold = 5*bar_width

def MakeDoublets(extracted, points):
    new_extracted = extracted
    new_unextracted = []
    
    for z0, x0 in points:
        for z1, x1 in extracted:
            if z0 == z1 and math.fabs(x0 - x1) <= width_threshold:
                if (z0, x0) not in new_extracted:
                    new_extracted.append((z0, x0))
                    
    for point in points:
        if point not in new_extracted:
            new_unextracted.append(point)
            
    assert len(new_extracted) >= len(extracted)
    assert len(new_extracted) + len(new_unextracted) == len(points)
    
    return new_extracted, new_unextracted

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

class CreateDAG():
    """ Create directed acyclic graph"""

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

                dag = Graph()
                gr = dag.CreateVertices(points)
                doc['graph']['gr0'] = markup.write(gr)
                gr = dag.CreateDirectedEdges(points, gr, layer_width)
                doc['graph']['gr1'] = markup.write(gr)

                # RemovePreexisting(previous)

                gr = dag.FindMST(gr)
                doc['graph']['gr2'] = markup.write(gr)

                print 'sort:', sorting.topological_sorting(gr)
                if gr.edges() == []:
                    continue

                grl, length = dag.LongestPath(gr)
                doc['graph']['gr3'] = markup.write(gr)

                if float(length) == 0.0:
                    doc['analyzable'] = False

                tracks[view][length] = grl #extracted
                tracks[view]['LEFTOVERS'] = gr.nodes()
                
            doc['tracks'] = tracks

            new_docs.append(doc)

        return new_docs

            
class ExtractTrack():
    """Extract track"""

    def __init__(self):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

    def ExtractFromView(self, zx_list):
        """Extract a track from a collection of points.

        @param xz_list

          A list of (z,x) coordinates.

        @return
          A list of the following values: a list of extracted points and length
        """

        #  Create a lookup table index by 'z' coordinate
        point_dict = {}
        for z0, x0 in zx_list:
            if z0 not in point_dict:
                point_dict[z0] = []
            point_dict[z0].append(x0)

        #  Grab points in 'z' with hits, and reverse sort
        keys = point_dict.keys()
        keys.sort()
        keys.reverse()

        #  If there are no points, just return now
        if len(keys) == 0:
            return [], 0.0

        length = 0.0
        extracted = []

        for z1 in keys:
            # Grab last point so we can make sure that we aren't stepping too
            # far between planes.  Note this is the -1 plane.
            if len(extracted) == 0:
                extracted = [(z1, point_dict[keys[0]][0])]
                continue
            
            z0, x0 = extracted[-1]

            best_x = None  #  Best 'x' in this plane

            leftovers = []

            for x1 in point_dict[z1]:
                # Set if unset
                if best_x == None:
                    best_x = x1

                # Differentials
                dz = z1 - z0
                dx = x1 - x0

                # Compute distance and compare to best: reject x1?
                if math.hypot(dz, dx) < math.hypot(z1 - z0, best_x - x0):
                    best_x = x1

            #  Make sure we aren't jumping too far.  If we are, throw the best
            # and leftovers into the unextracted bin
            if math.hypot(z1 - z0, best_x - x0) > 100.0:  # threshold, BUG FIXME, GDML
                break  # This should jump to final return

            # Compute length
            length += math.hypot(z1 - z0, best_x - x0)

            #  Store points
            extracted.append((z1, best_x))

        return extracted, length

    def Process(self, docs):
        new_docs = []  # Documents to be returned
        
        for doc in docs:
            if doc['type'] != 'track' or not doc['analyzable']:
                new_docs.append(doc)
                continue

            tracks = doc['tracks']
            for view in ['x', 'y']:
                points = tracks[view]['LEFTOVERS']

                extracted, l = self.ExtractFromView(points)
                extracted, unextracted = MakeDoublets(extracted, points)
                tracks[view][l] = extracted
                tracks[view]['LEFTOVERS'] = unextracted

                if 'length_%s' % view not in doc['classification']:
                    doc['classification']['length_%s' % view]   = l
                    
                if points == [] or extracted == []:
                    doc['analyzable'] = False

            doc['tracks'] = tracks

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
