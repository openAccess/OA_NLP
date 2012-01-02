'''
'''
from __future__ import division
import os, re, nltk, json
from datetime import datetime
from gitPLoS.search.query import articleUrl, articleXML

# These fields are required for the corpus
ReturnFields = 'id,journal,publication_date,article_type,author,subject,title,abstract,body'

class Builder():

    def __init__(self, query, corpus_name='myCorpus') :
	self.corpus_info = {}
        self.corpus_info['name'] = corpus_name
	self.corpus_info['creation_date'] = datetime.now().isoformat()
	self.corpus_info['query'] = query
	self.corpus_info['fileids'] = {}
	self.corpus_info['categories'] = {}
	os.mkdir( corpus_name )
        return

    def build(self, doc_list, verbose=False):
	'''
        Create a json file for each doc returned by the query.
	:Then create a corpus info file.
	'''
	name = self.corpus_info['name']
	fileids = self.corpus_info['fileids']
	categories = self.corpus_info['categories']

        for doc in doc_list:
            doi = doc['id'] 
            fn = doi.replace('/','-') + '.json'
	    fd = open( name + '/' + fn, 'w' ) 
	    json.dump( doc, fd, indent=5 )
	    if verbose: print 'Added : ' + fn
	    fd.close()
            fileids[doi] = ( fn, articleUrl( doi ), articleXML( doi) )
	    print fileids[doi][0] + ' ' + fileids[doi][1] + ' ' + fileids[doi][2]
	    # Keep a hash of subjects and the id's associated with it
	    if 'subject' in doc:
	        for s in doc['subject']:
                    if s in categories:
		        categories[s].append( doi )
                    else:
                        categories[s] = [ doi ]
            else:
		if verbsoe: print 'id: %s article_type : %s do not have subjects' % \
                      ( doi, doc['article_type'] )
           
	# Output the corpus info
	if verbose:
            print 'Corpus Name: %s' % ( name )
	    print 'Creation Date: %s' % ( self.corpus_info['creation_date'] )
	    print 'Categories: %s' % ( categories.keys() )
        fd = open( name + '/corpus_info.json', 'w' )
	json.dump( self.corpus_info, fd, indent=5 )
	fd.close()
	return
