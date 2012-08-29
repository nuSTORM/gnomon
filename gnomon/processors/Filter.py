"""Filter routines"""

import logging

import numpy as np
import math
from gnomon.processors import Base
from gnomon.Configuration import RUNTIME_CONFIG as rc


class AppearanceCuts(Base.Processor):

    def process(self, docs):
        new_docs = []

        for doc in docs:
            if doc['type'] != 'track' or not doc['analyzable']:
                new_docs.append(doc)
                continue

            clsf = doc['classification']

            ###  Variables to cut on  ###
            #  Number of hit SCINTILLATOR planes
            n_planes = clsf['n_planes']

            # Curvature (ie. coefficient of z**2) in the bending plane 'u'
            curve = clsf['fit_poly']['u'][2]

            ###  Variables to return  ###

            is_interesting = False

            pass_cuts = {}
            pass_cuts['length'] = False
            pass_cuts['curve'] = False
            pass_cuts['all'] = False

            ###  Cuts ###

            if (n_planes > 200):
                pass_cuts['length'] = True

            if (curve < 0.5e-4):
                pass_cuts['curve'] = True

            pass_cuts['all'] = pass_cuts['length'] and pass_cuts['curve']

            ### Interesting ###
            try:
                #  NC events that pass the length cut are bizarre
                if doc['mc']['event_type']['nc'] and pass_cuts['length']:
                    is_interesting = True
            except:
                pass

            try:
                #  CC nu_e events that pass the length cut are bizarre
                if doc['mc']['event_type']['cc'] and \
                        doc['mc']['event_type']['incoming_neutrino'] == 12 and\
                        pass_cuts['length']:
                    is_interesting = True
            except:
                pass

            try:
                #  CC nu_mu_bar that bend wrong
                if doc['mc']['event_type']['cc'] and \
                        doc['mc']['event_type']['incoming_neutrino'] == -14 and\
                        pass_cuts['all']:
                    is_interesting = True
                    
                    if curve < -0.5e-4:
                        clsf['is_very_interesting'] = True
            except:
                pass

            

            ### Save ###

            clsf['is_interesting'] = is_interesting
            doc['classification'] = clsf

            if 'cuts' not in doc:
                doc['cuts'] = {}
            doc['cuts']['appearance'] = pass_cuts

            new_docs.append(doc)

        return new_docs


class SaveInteresting(Base.Processor):

    def process(self, docs):
        new_docs = []

        for doc in docs:
            is_interesting = False
            try:
                if doc['classification']['is_interesting']:
                    is_interesting = True
            except:
                pass

            if not is_interesting:
                del doc['tracks']

            new_docs.append(doc)

        return new_docs
