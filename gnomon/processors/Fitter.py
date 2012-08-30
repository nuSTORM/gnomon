"""Fitter routines"""

import logging

from scipy.optimize import leastsq
import numpy as np
import math
from gnomon.Graph import Graph
from gnomon.processors import Base
from gnomon.Configuration import RUNTIME_CONFIG as rc

import gnomon.MagneticField as MagneticField


class EmptyTrackFromDigits(Base.Processor):
    """ Prepare for track extraction """

    def process(self, docs):
        run = None
        event = None

        new_docs = []

        tracks = {'x': {}, 'y': {}}
        tracks['x']['LEFTOVERS'] = []
        tracks['y']['LEFTOVERS'] = []

        for doc in docs:
            if doc['type'] != 'digit':
                new_docs.append(doc)
                continue

            if event is None:
                event = doc['event']
            if run is None:
                run = doc['run']
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


class ClassifyVariables(Base.Processor):
    """Compute various variables

    For example, (nhit, Qsum) including MINOS variables"""

    def process(self, docs):
        #  These docs will be returned
        new_docs = []

        for doc in docs:
            if not doc['analyzable']:
                new_docs.append(doc)
                continue

            n_hits = 0
            n_hits_main_track = 0
            total_charge = 0
            planes_with_hits = set()  # z coordinate, no repeats

            Q_dict = {}  # key z, value list of q
            Q_dict_main_track = {}

            for view in ['x', 'y']:
                main_track = doc['classification']['lengths'][view][0]

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

            c['fraction_of_hits_in_main_track'] = float(
                n_hits_main_track) / n_hits

            # MINOS variables
            my_keys = Q_dict.keys()  # get z values
            my_keys.sort()           # sort by z
            trim_keys = my_keys[len(my_keys) / 3:]  # grab second 2/3
            Q_list = []     # these will be the passed 'q' values
            for key in trim_keys:  # for second 2/3 key
                for q in Q_dict[key]:  # grab each q
                    Q_list.append(q)   # then add to list
            minos_mean_pulse_height = float(sum(Q_list)) / len(Q_list)
            Q_list.sort()
            l = len(Q_list)
            Q_low = Q_list[:l / 2]
            Q_high = Q_list[l / 2:]
            mean_low = float(sum(Q_low)) / len(Q_low)
            mean_high = float(sum(Q_high)) / len(Q_high)

            trim_keys = my_keys[len(my_keys) / 2:]  # grab second half
            Q_list_track = []
            Q_list_all = []
            for key in trim_keys:
                for q in Q_dict[key]:
                    Q_list_all.append(q)

                if key in Q_dict_main_track:  # reduced set, may not be there
                    for q in Q_dict_main_track[key]:
                        Q_list_track.append(q)

            minos_vars = {}
            minos_vars['mean_strip_pulse_height'] = minos_mean_pulse_height
            minos_vars['mean_low'] = mean_low
            minos_vars['mean_high'] = mean_high
            minos_vars['signal_fluctuation'] = mean_low / mean_high
            minos_vars['transverse_profile'] = float(
                sum(Q_list_track)) / sum(Q_list_all)
            c['minos'] = minos_vars
            # end minos

            c['n_planes'] = len(planes_with_hits)

            doc['classification'] = c

            #del doc['tracks']

            new_docs.append(doc)

        return new_docs

class CombineViews(Base.Processor):
    """Combine x and y views"""

    def sort_points(self, points):
        """Take points (z,x,q) and sort by increasing z"""
        new_points = []
        z_lookup = {}
        for z, x, Q in points:
            z_lookup[z] = (z, x, Q)

        z_keys = z_lookup.keys()
        z_keys.sort()

        for key in z_keys:
            new_points.append(z_lookup[key])

        return new_points

    def process(self, docs):
        new_docs = []

        for doc in docs:
            clsf = doc['classification']

            #  Throw away if not analyzable track
            if 'type' not in doc or\
                    doc['type'] != 'track' or\
                    doc['analyzable'] is False:
                new_docs.append(doc)
                continue

            #  Require extracted tracks
            if 'lengths' not in clsf or\
                    'x' not in clsf['lengths'] or\
                    'y' not in clsf['lengths']:
                new_docs.append(doc)
                continue

            tracks = doc['tracks']


            lx = clsf['lengths']['x'][0]
            pts_x = tracks['x'][lx]
            pts_x = self.sort_points(pts_x)

            ly = clsf['lengths']['y'][0]
            pts_y = tracks['y'][ly]
            pts_y = self.sort_points(pts_y)

            new_points = []

            while len(pts_y) > 0 and len(pts_x) > 0:
                # While there are still points to match up

                z_x, trans_x, Q_x = pts_x.pop()
                z_y, trans_y, Q_y = pts_y.pop()

                if math.fabs(z_x - z_y) < rc['thickness_layer']:
                    #  If they are in the same layer
                    new_z = (z_x + z_y) / 2.0
                    new_r = math.hypot(trans_x, trans_y)
                    new_theta = math.atan2(trans_y, trans_x) # y first according to pydocs
                    new_Q = Q_x + Q_y
                    new_points.append((new_z, new_r, new_Q))
                else:
                    # Otherwise, toss out most downstream point and keep the
                    # upstream point.
                    if z_x > z_y:
                        pts_y.append((z_y, trans_y, Q_y))
                    else:
                        pts_x.append((z_x, trans_x, Q_x))

            tracks['combined'] = new_points

            # Save our modified tracks
            doc['tracks'] = tracks
            new_docs.append(doc)

        return new_docs


class ExtractTracks(Base.Processor):
    """Extract tracks per view with graph theoretic concepts"""

    def process(self, docs):
        run = None
        event = None

        new_docs = []

        nodes = []

        for doc in docs:
            if doc['type'] != 'track':
                new_docs.append(doc)
                continue

            tracks = doc['tracks']

            for view in ['x', 'y']:
                self.log.info('Working on view %s' % view)
                points = tracks[view]['LEFTOVERS']

                dag = Graph()
                gr = dag.CreateVertices(points)
                gr = dag.CreateDirectedEdges(points, gr, rc['thickness_layer'])
                if gr.edges() == []:
                    doc['analyzable'] = False
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

                lengths = [length1, length2, length3]

                if 'lengths' not in doc['classification']:
                    doc['classification']['lengths'] = {}

                doc['classification']['lengths'][view] = lengths

            doc['tracks'] = tracks

            new_docs.append(doc)

        return new_docs


class VlenfPolynomialFitter(Base.Processor):

    def __init__(self):
        Base.Processor.__init__(self)
        self.field = MagneticField.WandsToroidField('+')

    def Fit(self, zxq):
        """Perform a 2D fit on 2D points then return parameters

   :param zxq: A list where each element is (z, transverse, charge)
   """
        z, trans, Q = zip(*zxq)

        assert len(trans) == len(z)
        ndf = len(z) - 3

        z = np.array(z)
        trans = np.array(trans)

        def dbexpl(t, p):
            return(p[0] - p[1] * t + p[2] * t ** 2)

        def residuals(p, data, t):
            err = data - dbexpl(t, p)
            return err

        doc = {}

        try:
            assert ndf > 0

            p0 = [1, 0, 0]  # initial guesses
            pbest = leastsq(residuals, p0, args=(trans, z), full_output=1)
            bestparams = pbest[0]
            good_of_fit = sum(pbest[2]['fvec'] ** 2)
            good_of_fit = float(good_of_fit / ndf)
            doc['params'] = list(bestparams)
            doc['gof'] = good_of_fit
        except:
            doc['gof'] = 'FAIL'
            doc['params'] = [0, 0, 0]

        return doc

    def _rotate(self, x, y):
        self.log.debug('Rotating using x=%s and y=%s' % (str(x), str(y)))
        value = [0, 0, 0]
        for i in range(3):
            value[i] = x[0] * x[i] + y[0] * y[i]
            value[i] /= math.hypot(x[0], y[0])
        return value

    def _get_last_transverse_over_list(self, zxq):
        """ Get transverse coord at highest z

        :param zx: A list where each element is (z, transverse, charge)
        """
        z_max = None
        x_of_interest = None

        for z, x, q in zxq:
            if z == None or z > z_max:
                x_of_interest = x

        return x_of_interest


    def process(self, docs):
        new_docs = []
        for doc in docs:
            #  Checking state
            if 'type' not in doc or\
                    doc['type'] != 'track' or\
                    doc['analyzable'] is False:
                new_docs.append(doc)
                continue

            clsf = doc['classification']

            if 'tracks' not in doc:
                self.log.info('Skipping since no tracks found...')
                new_docs.append(doc)
                continue

            if 'lengths' not in clsf:
                self.log.info('Skipping no extracted tracks to fit')
                new_docs.append(doc)
                continue

            tracks = doc['tracks']

            rf = {}  # raw fit
            rf['gof'] = {}

            for view in ['x', 'y', 'combined']:

                if view == 'combined':
                    points = tracks[view]
                else:
                    l = clsf['lengths'][view][0]
                    points = tracks[view][l]

                try:
                    fit_doc = self.Fit(points)
                except Exception, err:
                    self.log.exception('Error from polynomial fitter:')
                    #  Something bad happened... mark event not analyzable
                    doc['analyzable'] = False

                if fit_doc['gof'] != 'FAIL':
                    rf['gof'][view] = fit_doc['gof']
                else: # fail
                    self.log.warning("Fit in %s failed" % view)
                    doc['analyzable'] = False
                    continue

                if len(fit_doc['params']) == 3:
                    rf[view] = fit_doc['params']
                else: # fail
                    self.log.error("Fit in %s failed; didn't receive params" % view)
                    doc['analyzable'] = False
                    continue

            if doc['analyzable']:
                # Rotate fits to bending plane
                x0, x1, x2 = rf['x']
                y0, y1, y2 = rf['y']            
                rf['u'] = self._rotate(rf['x'], rf['y'])

            # Save
            clsf['fit_poly'] = rf
            doc['classification'] = clsf
            new_docs.append(doc)

        return new_docs
