"""Classify"""

import logging
import sys
import math

class ComputeHadronicEnergy:
    def Shutdown(self):
        pass

    def Process(self, docs):
        new_docs = []
        for doc in docs:
            # Skip if not track
            if doc['type'] != 'track':
                new_docs.append(doc)
                continue

            if 'classification' not in doc:
                doc['classification'] = {}


            E_hadron = 0.0

            for view_name in ['x', 'y']:
                whole_view = doc[view_name]
                good_view = doc['extracted_%s' % view_name]
                
                # Inefficient, but clean code
                all_points = zip(whole_view['z'], whole_view['trans'], whole_view['E'])
                good_points = zip(good_view['z'], good_view['trans'], good_view['E'])

                if len(all_points) < 3:
                    continue

                # O(n**2) algorithm, yuck.
                for z0, x0, E0 in all_points:
                    is_good = False
                    for z1, x1, E1 in good_points:
                        if z1 == z0 and x1 == x0:
                            is_good = True

                    if not is_good:
                        E_hadron += E0

                doc['classification']['fraction_of_track_used_%s' % view_name] = float(len(good_points))/len(all_points)

            doc['classification']['E_hadron'] = E_hadron

            new_docs.append(doc)

        return new_docs

class ContinousLength:
    def Shutdown(self):
        pass
    
    def Process(self, docs):
        new_docs = []
        for doc in docs:
            # Skip if not track
            if doc['type'] != 'track':
                new_docs.append(doc)
                continue
                
            if 'classification' not in doc:
                doc['classification'] = {}
                    
            if not doc['analyzable']:
                doc['classification']['continous_length'] = 'FAILED'
                continue
            

            points = doc['x']['z'] + doc['y']['z']
            points.sort()

            layer_width = 30 # mm
            max_length = None
            point_min  = None
            point_last = None
            
            for point in points:
                if point_min == None:
                    point_min = point

                if point_last == None:
                    point_last = point
                
                if point - point_last > layer_width:
                    point_min  = None
                    point_last = None
                else:
                    if point - point_min > max_length:
                        max_length = point - point_min
                    point_last = point
            
            doc['classification']['continous_length'] = max_length
            
            new_docs.append(doc)
            
        return new_docs
        
