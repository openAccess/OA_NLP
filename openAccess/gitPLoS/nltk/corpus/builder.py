'''
'''
from __future__ import division
import os, re, nltk, json
from util import doi2fn
from datetime import datetime
from gitPLoS.search.query import articleUrl, articleXML

# These fields are required for the corpus
QUERY_RTN_FLDS = ['id','journal','publication_date',
                  'article_type','author','subject',
		  'title','abstract','body',
                 ]
DFLT_ROOT = './'
DFLT_CORPUS_NAME = 'myCorpus'

class Builder(object):
    """
    A corpus builder.
    """
    def __init__(self, query, root=DFLT_ROOT, name=DFLT_CORPUS_NAME):
        """
        """
	self.name = name
	self.root = root
	self.corpus_info = info = {}
        info['name'] = name
	info['creation_date'] = datetime.now().isoformat()
	info['query'] = query
	info['article_link'] = {}
	info['xml_link'] = {}
	info['f2c'] = {}
	info['c2f'] = {}

	os.mkdir( '%s/%s' % (root, name) )
        return

    def build(self, docs):
	"""
        Create a json file for each doc returned by the query.
	Then create a corpus info file.

	@type docs: list
	@param docs: A list containing the results of a PLoS search query.
	             Each item is a dictionary with QUERY_RTN_FLDS as keys.

        @return: Nothing
	"""
	name = self.name
	root = self.root
	info = self.corpus_info
	f2cmap = info['f2c']
	c2fmap = info['c2f']
	amap = info['article_link']
	xmap = info['xml_link']

	# Builde all the list and mappings
        for doc in docs:
            doi = doc['id']
            # If the doc has not subject, add []
            if 'subject' not in doc: 
                doc['subject'] = []
	    
	    # File id -> [ c1, c2, .... ]
            f2cmap[doi] = subjs = doc['subject']
	    # Category -> [ f1, f2, .... ]
	    for s in subjs:
	       if s in c2fmap:
                  c2fmap[s].append(doi)
	       else:
                  c2fmap[s] = [ doi ]
            # doi -> article link
	    amap[doi] = articleUrl(doi)
	    # doi -> artilce xml link
	    xmap[doi] = articleXML(doi)
        
	fnames = [ doi2fn(doi) for doi in f2cmap.keys() ]
        fnames_docs = zip(fnames, docs)
        
        # Dump all the docs into individual files.
	for fn,doc in fnames_docs:
            fd = open( '%s/%s/%s' % (root,name,fn), 'w')
	    json.dump(doc, fd, indent=5)
	    fd.close()
        # Dump the info file.
        fd = open( '%s/%s/corpus_info.json' % (root, name), 'w' )
	json.dump( info, fd, indent=5 )
	fd.close()
	return
