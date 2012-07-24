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
            counts_adc = doc['counts_adc']

            if view == 'X':
                track_point = (position['z'], position['x'], counts_adc)
                tracks['x']['LEFTOVERS'].append(track_point)
            else:
                track_point = (position['z'], position['y'], counts_adc)
                tracks['y']['LEFTOVERS'].append(track_point)

        doc = {}
        doc['type'] = 'track'

        doc['run'] = run
        doc['event'] = event

        doc['analyzable'] = True
        doc['classification'] = {}
        doc['tracks'] = tracks

        new_docs.append(doc)

        return new_docs


class Containment():
        """Penetration Depth

        Measured in terms of iron planes.  95% containment computed
        """

        def Shutdown(self):
            pass

        def Process(self, docs):
            new_docs = []

            for doc in docs:
                if not doc['analyzable']:
                    continue

                hits = {}  # key: z, value: number of hits
                nhits = 0

                for view in ['x', 'y']:
                    main_track = doc['classification']['%s_length1' % view]

                    for track, points in doc['tracks'][view].iteritems():
                        for z, x, Q in points:
                            if z not in hits:
                                hits[z] = 0
                            hits[z] += 1
                            nhits += 1


                z_min = None

                z_keys = hits.keys()
                z_keys.sort()


                current_sum = 0

                contained_95 = None
                
                for z in z_keys:
                    if z_min == None or z < z_min:
                        z_min = z

                    current_sum += hits[z]

                    if contained_95 == None:  # If already found, skip
                        if float(current_sum) / nhits > 0.95:
                            contained_95 = z - z_min

                doc['classification']['containment'] = contained_95
                
                new_docs.append(doc)
        
            return new_docs
                
class EnergyDeposited():
    """ blah """

    def Shutdown(self):
        pass

    def Process(self, docs):
        new_docs = []   
        
        for doc in docs:
            if not doc['analyzable']:
                continue

            n_hits = 0
            n_hits_main_track = 0
            total_charge = 0
            planes_with_hits = set() # z coordinate, no repeats

            Q_dict = {}  # key z, value list of q
            Q_dict_main_track = {}

            for view in ['x', 'y']:
                main_track = doc['classification']['%s_length1' % view]

                for track, points in doc['tracks'][view].iteritems():
                    for z, x, Q in points:
                        total_charge += Q
                        n_hits += 1

                        # MINOS stuff
                        if z not in Q_dict.keys():
                            Q_dict[z] = []
                        Q_dict[z].append(Q)

                        if track == main_track:
                            n_hits_main_track += 1
                            if z not in Q_dict_main_track.keys():
                                Q_dict_main_track[z] = []
                            Q_dict_main_track[z].append(Q)

                        planes_with_hits.add(z)

            c = doc['classification']

            c['Qsum'] = total_charge
            c['n_hits'] = n_hits

            c['fraction_of_hits_in_main_track'] = float(n_hits_main_track)/n_hits

            # MINOS variables
            my_keys = Q_dict.keys()  # get z values
            my_keys.sort()           # sort by z
            trim_keys = my_keys[len(my_keys)/3:]  # grab second 2/3
            Q_list = []     # these will be the passed 'q' values
            for key in trim_keys:  # for second 2/3 key
                for q in Q_dict[key]:  # grab each q
                    Q_list.append(q)   # then add to list
            minos_mean_pulse_height = float(sum(Q_list))/len(Q_list)
            Q_list.sort()
            l = len(Q_list)
            Q_low = Q_list[:l/2]
            Q_high = Q_list[l/2:]
            mean_low = float(sum(Q_low))/len(Q_low)
            mean_high = float(sum(Q_high))/len(Q_high)

            trim_keys = my_keys[len(my_keys)/2:]  # grab second half
            Q_list_track = []
            Q_list_all= []
            for key in trim_keys:
                for q in Q_dict[key]:
                    Q_list_all.append(q)

                if key in Q_dict_main_track:  # reduced set, so may not be there
                    for q in Q_dict_main_track[key]:
                        Q_list_track.append(q)

            minos_vars = {}
            minos_vars['n_planes'] = len(planes_with_hits)
            minos_vars['mean_strip_pulse_height'] = minos_mean_pulse_height
            minos_vars['mean_low'] = mean_low
            minos_vars['mean_high'] = mean_high
            minos_vars['signal_fluctuation'] = mean_low/mean_high
            minos_vars['transverse_profile'] = float(sum(Q_list_track))/sum(Q_list_all)
            c['minos'] = minos_vars

            # end minos

            doc['classification'] = c

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

                parent_node = dag.FindParentNode(gr)
                gr3, length3, gr = dag.ComputeLongestPath(gr, parent_node)

                if float(length1) == 0.0:
                    doc['analyzable'] = False

                tracks[view][length1] = gr1
                tracks[view][length2] = gr2
                tracks[view][length3] = gr3
                tracks[view]['LEFTOVERS'] = gr.nodes()

                doc['classification']['%s_length1' % view] = length1
                doc['classification']['%s_length2' % view] = length2
                doc['classification']['%s_length3' % view] = length3

            doc['tracks'] = tracks

            new_docs.append(doc)

        return new_docs


class VlenfPolynomialFitter():

    def __init__(self):
        self.log = logging.getLogger('root')
        self.log = self.log.getChild(self.__class__.__name__)

        self.tracks = []

    def Shutdown(self):
        pass

    def Fit(self, zx):
        """Returns results of fit

        """

        z, trans, Q = zip(*zx)

        assert len(trans) == len(z)
        ndf = len(z) - 3

        z = np.array(z)
        trans = np.array(trans)

        def dbexpl(t,p):
            return(p[0] - p[1] * t + p[2] * t**2)

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

            if 'x_length1' not in doc['classification'] or\
                   'y_length1' not in doc['classification']:
                continue

            lx = doc['classification']['x_length1']
            fitx_doc = self.Fit(tracks['x'][lx])
            ly = doc['classification']['y_length1']
            fity_doc = self.Fit(tracks['y'][ly])

            for fit_doc in [fitx_doc, fity_doc]:
                assert len(fit_doc['params']) == 3

            clsf = doc['classification']

            clsf['gof_x'] = fitx_doc['gof']
            clsf['gof_y'] = fity_doc['gof']

            try:
                assert clsf['gof_x'] != 'FAIL'
                assert clsf['gof_y'] != 'FAIL'
                doc['analyzable'] = True
                
                rf = {}  #  raw fit
                rf['x'] = fitx_doc['params']
                rf['y'] = fity_doc['params']
                rf['x2'] = fitx_doc['params'][2]

                rf['y0'] = fity_doc['params'][0]
                rf['y1'] = fity_doc['params'][1]
                rf['y2'] = fity_doc['params'][2]

                clsf['fit_poly'] = rf
                
                clsf['curve'] = rf['x0'] * rf['x2'] + rf['y0'] * rf['y2']
                clsf['curve'] = clsf['curve'] / math.hypot(rf['x0'], rf['y0'])

                
            except:
                doc['analyzable'] = False
            
            doc['classification'] = clsf

            new_docs.append(doc)
        return new_docs
