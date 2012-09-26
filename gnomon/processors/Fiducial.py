"""Determine distance to fiducial boundary"""

import numpy as np
import math
from gnomon.processors import Base


class FiducialCuts(Base.Processor):
    def distance_to_boundaries(self, z, x):
        # config is inherited from the parent class
        self.z_extent = self.runtime_config['layers'] * self.runtime_config['thickness_layer']
        self.x_extent = self.runtime_config['bars'] * self.runtime_config['width']

        distances = {}
        distances['transverse_inner'] = math.fabs(x)
        distances['transverse_outer'] = self.x_extent - math.fabs(x)
        distances['longitudinal_downstream'] = self.z_extent / 2 - z
        distances['longitudinal_upstream'] = z + self.z_extent / 2
        return distances

    def apply_cuts(self, distances):
        cuts = {}
        pass_all = True

        for key, val in distances.iteritems():
            if val < self.config['fiducial'][key]:
                cuts[key] = False
            else:
                cuts[key] = True

            pass_all = pass_all and cuts[key]

        cuts['all'] = pass_all

        return cuts


    def process(self, docs):
        new_docs = []

        # Loop over documents (most likely tracks)
        for doc in docs:
            # If not analyzable or track, skip
            if doc['type'] != 'track' or not doc['analyzable']:
                # Keep the doc though since others may want down the pipeline
                new_docs.append(doc)
                continue

            event_cuts = {}

            for view in ['x', 'y']:
                #  Ensure that tracks haven't already been extracted (ex. muon)
                if len(doc['tracks'][view].keys()) > 1:
                    self.log.error('Expected unclassified tracks')
                    self.log.error('Please run before extracting tracks')
                    raise ValueError("Expected unclassified tracks")

                #  Leftovers should be all hits
                points = doc['tracks'][view]['LEFTOVERS']

                for z, x, Q in points:
                    distance = self.distance_to_boundaries(z, x)
                    point_cuts = self.apply_cuts(distance)

                    for key, value in point_cuts.iteritems():
                        if key not in event_cuts:
                            event_cuts[key] = True

                        event_cuts[key] = event_cuts[key] and value


            ### Save ###

            if 'cuts' not in doc:
                doc['cuts'] = {}
            doc['cuts']['fiducial'] = event_cuts

            new_docs.append(doc)

        return new_docs
