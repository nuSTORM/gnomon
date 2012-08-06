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
            minos_vars['n_planes'] = len(planes_with_hits)
            minos_vars['mean_strip_pulse_height'] = minos_mean_pulse_height
            minos_vars['mean_low'] = mean_low
            minos_vars['mean_high'] = mean_high
            minos_vars['signal_fluctuation'] = mean_low / mean_high
            minos_vars['transverse_profile'] = float(
                sum(Q_list_track)) / sum(Q_list_all)
            c['minos'] = minos_vars

            # end minos

            doc['classification'] = c

            del doc['tracks']

            new_docs.append(doc)

        return new_docs

class ContinousLongitudinalLength(Base.Processor):
    """Extract the continous longitudinal length
    """
    def process(self, docs):
        #  These docs will be returned
        new_docs = []
        
        for doc in docs:
            if not doc['analyzable'] or doc['type'] != 'track':
                new_docs.append(doc)
                continue

            scint_planes_with_hits = set()  # z coordinate, no repeats
            
            for view in ['x', 'y']:
                if len(doc['tracks'][view].keys()) > 1:
                    self.log.error('Expected unclassified tracks')
                    self.log.error('Please run before extracting tracks')

                points = doc['tracks'][view]['LEFTOVERS']
                for z, x, Q in points:
                    scint_planes_with_hits.add(z)

            #  Convert to list so can sort...
            scint_planes_with_hits = list(scint_planes_with_hits)
                    
            scint_planes_with_hits.sort()
                
            #  Iterate over the hits computing continous lengths, compare
            # against maximum.
            max_length = None
            this_length = 0
            for i, z in enumerate(scint_planes_with_hits):
                if i + 1 >= len(scint_planes_with_hits):
                    break

                dz = scint_planes_with_hits[i+1] - z
                if dz <= rc['thickness_layer']:
                    this_length += dz
                    if this_length > max_length or max_length is None:
                        max_length = this_length
                else:
                    print i, z, dz
                    this_length = 0

            doc['classification']['longitudinal_length'] = max_length
            doc['classification']['longitudinal_length2'] = scint_planes_with_hits[0] - scint_planes_with_hits[-1]
            new_docs.append(doc)
        return new_docs

class ExtractTracks(Base.Processor):
    """Extract tracks with graph theoretic concepts"""

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

    def Fit(self, zx):
        """Returns results of fit

        """

        z, trans, Q = zip(*zx)

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
        value = [0, 0, 0]
        for i in range(3):
            value[i] = x[0] * x[i] + y[0] * y[i]
            value[i] /= math.hypot(x[0], y[0])
        return value

    def process(self, docs):
        new_docs = []
        for doc in docs:
            if 'type' not in doc or\
                    doc['type'] != 'track' or\
                    doc['analyzable'] is False:
                new_docs.append(doc)
                continue

            clsf = doc['classification']

            try:

                tracks = doc['tracks']

                assert 'lengths' in clsf

                lx = clsf['lengths']['x'][0]
                fitx_doc = self.Fit(tracks['x'][lx])
                ly = clsf['lengths']['y'][0]
                fity_doc = self.Fit(tracks['y'][ly])

                for fit_doc in [fitx_doc, fity_doc]:
                    assert len(fit_doc['params']) == 3

                assert fitx_doc['gof'] != 'FAIL', "Fit failed"
                assert fity_doc['gof'] != 'FAIL', "Fit failed"
                doc['analyzable'] = True

                rf = {}  # raw fit

                rf['gof'] = {'x': fitx_doc['gof'], 'y': fity_doc['gof']}

                rf['x'] = fitx_doc['params']
                x0, x1, x2 = rf['x']

                rf['y'] = fity_doc['params']
                y0, y1, y2 = rf['y']

                rf['u'] = self._rotate(rf['x'], rf['y'])

                rf['R'] = (
                    1 + rf['u'][1] ** 2) ** (1.5) / (2 * rf['u'][2])  # mm
                rf['B'] = self.field.PhenomModel(math.hypot(x0, y0))

                rf['p_MeV'] = 300 * rf['B'] * rf['R'] / 1000  # MeV

                clsf['fit_poly'] = rf

            except Exception, err:
                self.log.exception('Error from polynomial fitter:')
                #  Something bad happened... mark event not analyzable
                doc['analyzable'] = False

            doc['classification'] = clsf

            new_docs.append(doc)

        return new_docs
