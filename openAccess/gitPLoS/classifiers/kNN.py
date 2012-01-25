#!/usr/bin/env python
# openAccess: getPLoS
#
#Copyright (c) 2001-2012 openAccess Project
# Author: Bill OConnor
# URL: <https://github.com/openAccess/gitPLoS>
# For license information, see LICENSE.TXT
#
"""
    Description
    ===========
    
    kNN - k Nearest Neighbor classifier. Takes a list of 
    (category, [values]) tuples as training data. Data points
    are classified by calculating the distance from each 
    point in the training data. The distances are sorted giving
    higher preference to smallest distances. Then k shortest
    distances are used to calculate the weights for each class.
"""
from __future__ import division
from math import sqrt

def _vec_minkowski(p, q, e):
    l = [ abs(p[i] - q[i])**e for i in xrange(len(q)) ]
    return sum(l)**(1/e)

def _vec_chebyshev_dist(p, q):
    return max([ abs(p[i]-q[i]) for i in xrange(len(q)) ]) 

def _vec_manhattan_dist(p, q):
    return sum([ abs(p[i]-q[i]) for i in xrange(len(q)) ])

def _vec_euclidean_dist(p, q):
    """
    Euclidean Vector distance function. 
    """
    l = [ p[i]-q[i] for i in xrange(len(p)) ]
    return sqrt(sum([ d*d for d in l ]))

def _euclidean_dist(x, y):
    """
    Scalar distance function.
    """
    return abs(x-y)

def _eq_weight(x, y):
    return 1

class kNN(object):
    """
    k Nearest Neighbor classifier.
    """
    def __init__(self, data, k):
        """
	data - a list of (category, [values] ) tuples.
        """
        self.data = data    # list of (category, value) tuples used for training
        self.k = k

    def calculate(self, x, wt_fn=_eq_weight, dist_fn=_vec_euclidean_dist):
        """
        """
        x_lst = x
        if not isinstance(x, list):
            x_lst = [x]

        # Calculate distance tuples (distance,category,value)
        dist = [ (dist_fn(x_lst, v), c, v) for c,v in self.data ]
        # Sort by distance, shortest first. 
	dist.sort()
        weights = { c : 0.0 for c,v in data }
	for d,c,v in dist[:self.k]:
            weights[c] += wt_fn(x,v) 

        return sorted([ (v, c) for c,v in weights.iteritems() ], reverse=True)

    def classify(self, x, **kwargs):
        """
        """
        class_lst = self.calculate(x, **kwargs)
	if len(class_lst) > 0:
            return class_lst[0]
        return None
