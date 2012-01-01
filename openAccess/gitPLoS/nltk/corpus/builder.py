'''
'''
from __future__ import division
import os, re, nltk, pprint, json
from datetime import datetime

# These fields are required for the corpus
ReturnFields = 'id,journal,publication_date,author,subject,title,abstract,body'

class Builder():

    def __init__(self, query, corpus_name='myCorpus') :
	self.corpus_info = {}
        self.corpus_info['name'] = corpus_name
	self.corpus_info['creation_date'] = datetime.now().isoformat()
	self.corpus_info['query'] = query
	self.corpus_name = corpus_name
	self.fileids = []
	self.corpus_info['fileids'] = self.fileids
	os.mkdir( corpus_name )
        return

    def build(self, doc_list, verbose=False):
	'''
        Create a json file for each doc returned by the query.
	Then create a corpus info file.
	'''
        for doc in doc_list:
            fn = doc['id'].replace('/','-') + '.json'
	    fd = open( self.corpus_name + '/' + fn, 'w')
	    json.dump( doc, fd, indent=5 )
	    if verbose: print 'Added : ' + fn
	    fd.close()
            self.fileids.append(fn)
	# Output the corpus info
        fd = open( self.corpus_name + '/corpus_info.json', 'w')
	json.dump( self.corpus_info, fd, indent=5 )
	fd.close()
	return
