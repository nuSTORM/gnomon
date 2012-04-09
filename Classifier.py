"""Classify"""

import logging
import sys

class RecursiveLength:
    def Shutdown(self):
        pass

    def getMaxDistance(z, points_x, points_y):
        for 

    def Process(self, docs):
        new_docs = []
        for doc in docs:
            # Skip if not track
            if doc['type'] != 'track':
                new_docs.append(doc)
                continue

            if 'classification' not in doc:
                doc['classification'] = {}



            points_z = doc['x']['z'] + doc['y']['z']

            points_z.sort()
            points_z.reverse()

            doc['classification']['length'] = value_max - value_min

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
        
