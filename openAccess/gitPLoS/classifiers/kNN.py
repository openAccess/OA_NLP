#!/usr/bin/env python
#
#
"""
"""
from __future__ import division
import math
from collections import *

def _vec_minkowski(p, q, e):
    l = [ abs(p[i] - q[i])**e for i in xrange(len(q)) ]
    return sum(l)**(1/e)

def _vec_chebyshev_dist(p, q):
    return max([ abs(p[i]-q[i]) for i in xrange(len(q)) ]) 

def _vec_manhattan_dist(p, q):
    return sum([ abs(p[i]-q[i]) for i in xrange(len(q)) ])

def _vec_euclidean_dist(p, q):
    """
    Vector distance function. 
    """
    l = [ p[i]-q[i] for i in xrange(len(p)) ]
    return math.sqrt(sum([ d*d for d in l ]))

def _euclidean_dist(x, y):
    """
    Scalar distance function.
    """
    return abs(x-y)

def _eq_weight(x, y):
    return 1

class kNN(object):
    """
    """
    def __init__(self, data, k):
        """
	data - a list of (category, value) tuples.
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

if __name__ == '__main__':
    data = [ ('a', [1.0]), ('b', [3.0]), ('b', [4.0]), ('a', [1.5]), ('c', [3.5]) ]
    knn = kNN(data,3)
    r = knn.calculate([4.0])
    print knn.classify([4.0])
    print r

