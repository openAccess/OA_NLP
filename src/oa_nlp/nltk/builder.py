# -*- coding: utf-8 -*-
# Open Access Natural Language Processing: NLTK Corpus Builder 
#
# Copyright (C) 2011-2014 OA_NLP Project
# Author: Bill OConnor <wtoconnor@gmail.com>
# For license information, see LICENSE.TXT
"""



"""
from __future__ import division
import os, re, nltk, json
import codecs
from util import doi2fn
from datetime import datetime
from ao_nlp.plos_api.solr as oa_nlp import article_page_url, article_xml_url

# These fields are required for the corpus
QUERY_RTN_FLDS = ['id','journal','publication_date',
                  'article_type','author','subject',
                  'title','abstract','body','editor',
                 ]

class Builder(object):
  """
  OA_NLP corpus builder for NLTK compatibility.
  """
  def __init__(self, query, root):
        self._root = root
        self._corpus_info = {
          'creation_date' : datetime.now().isoformat(),
          'query'         : query,
          'article_link'  : dict(),
          'xml_link'      : dict(),
          'c2d'           : dict(),
          'd2c'           : dict(),
	  'd2info'        : dict(),
        }

        os.mkdir( root )
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
        self.add(docs)
        self.finalize()
        return

    def add(self, docs):
        """
        Create a json file for each doc in the document list.

        @type docs: list
        @param docs: A list containing the results of a PLoS search query.
                     Each item is a dictionary with QUERY_RTN_FLDS as keys.

        @return: Nothing
        """
        root = self._root
        info = self._corpus_info
        d2cmap = {}; c2dmap = defaultdict(list); d2infomap = {}
        amap = info['article_link']
        xmap = info['xml_link']
        # Build all the lists and mappings
        for doc in docs:
            doi = doc['id']
            # If the doc has not subject, add []
            if 'subject' not in doc: 
                doc['subject'] = []
            
            # File id -> [ c1, c2, .... ]
            d2cmap[doi] = subjs = doc['subject']
            # Category -> [ f1, f2, .... ]
            for s in subjs:
                c2dmap[s].append(doi)
            # doi -> article link
            amap[doi] = articleUrl(doi)
            # doi -> artilce xml link
            xmap[doi] = articleXML(doi)
	    # Depending on the article type some of these might not exist.
	    jrnl = doc['journal'] if 'journal' in doc else ''
	    pub_date = doc['publication_date'] if 'publication_date' in doc else ''
	    atype = doc['article_type'] if 'article_type' in doc else ''
	    title = doc['title'] if 'title' in doc else ''
	    author = doc['author'] if 'author' in doc else []

            d2infomap[doi] =  (jrnl, pub_date, atype, title, author)
       
        fnames = [ doi2fn(doi, 'body') for doi in d2cmap.keys() ]
        fnames_docs = zip(fnames, docs)
        
        # Dump doc_part 'body' into individual files.
        for fn,doc in fnames_docs:
            fd = codecs.open( '%s/%s' % (root,fn), 'w', encoding='utf-8')
	    fd.write(doc['body'])
            fd.close()

        fnames = [ doi2fn(doi, 'abstract') for doi in d2cmap.keys() ]
        fnames_docs = zip(fnames, docs)
        
        # Dump doc_part 'abstract' into individual files.
        for fn,doc in fnames_docs:
            fd = codecs.open( '%s/%s' % (root,fn), 'w', encoding='utf-8')
	    fd.write(doc['abstract'][0])
            fd.close()

        # Update the corpus info 
        info['d2c'].update(d2cmap)

        c2d = info['c2d']
        for k,v in c2dmap.iteritems():
            if k not in c2d:
                c2d[k] = []
            c2d[k].extend(v)

	info['d2info'].update(d2infomap)
        return
 
    def finalize(self):
        """
        Save the corpus info file.
        """
        # Dump the info file.
        fd = open( '%s/corpus_info.json' % (self._root), 'w' )
        json.dump( self._corpus_info, fd, indent=5 )
        fd.close()
        return
