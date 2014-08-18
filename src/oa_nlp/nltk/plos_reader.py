#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
oa_nlp.nltk.plos_reader

PLOS solr api. http://api.plos.org/search

  Description:
  ===========

  PlosReader is loosely modeled on ntlk.corpus.api.CategorizedPlaintextCorpusReader.
  A corpus created using the plos_reader.py. There are 3 different types of corpora
  created "full', "partial" and "training". The the "full" corpus includes both the
  partial and training articles. The "partial" is intended for experimentation. The
  "training" corpus is a smaller subset of "full" that is not in "partial" that
  can be used to train classifiers.  
    
  In a sense there is no such thing as a definative PLoS corpus. A corpus can
  be created based on a set of selection criteria submitted to the Solr search
  server. The document doi, journal, authors, subjects, publication date, body, 
  abstract and URL to the original article XML are included in the meta-data. 
  The Plos_reader provides access to this info as well as some standard methods 
  in nltk.readers.
    
  An NTLK compatible corpus reader. PLoS articles are identified by a Digital
  Object Identifier (DOI) and have a 'body' containing the text of the article 
  and a 'abstract'. Since working with abstracts and/or article bodies might be 
  useful, both are incorporated into the corpus. The actual file identifiers are 
  follow the pattern 'DOI-doc_part.txt', where DOI is the article DOI with '/' 
  replaced by '-' and doc_part is either 'body' or 'abstract'. When a new 
  Plosreader is initialized the NLTK file identifiers are generateid using doc_part
  and DOIs. The NLTK super class is initialized using these ids. From that point on 
  PlosReader will have all the functionality of the CategorizedPlaintextCorpusReader.

Usage:
  plos_reader.py [options]  COMMAND CORPUS_NAME
    
 COMMANDS:   
   art-info     dump the article information for each article.
   
   art-page     list the doi and url to the article.
   
   art-xml      list doi and url or the xml for the article.
   
   body-fn      list the doi and file name for the body of the document. 
   
   abst-fn      list the doi and file name for the abstract of the document.

Examples:
  plos_reader.py  -c training abst-fn new-corpus

Options:
  -h --help                show this help and exit.

  -d --doc-part=<part>     the document part. "abstract' and "body"
                           are supported.
                           [default: abstract]
                          
  -c --corpus-type=<ctype> the corpus type. "full", "partial" and
                           "training" are supported. 
                           [default: full]

Author:
  Bill OConnor

License:
  Apache 2.0
  
Copyright (c) 2012-2014 OA_NLP Project
    
"""
import json
from util import doi2fn
from nltk.corpus.reader.plaintext import  CategorizedPlaintextCorpusReader

__version__ = '0.1.0'
__author__ = 'Bill OConnor'

class Plos_reader(CategorizedPlaintextCorpusReader):
  """
  """
  def __init__(self, root, **kwargs):
    """ 
	Initialize a PLoS reader with a specific corpus. Corpus 
	information is contained in 'root/corpus_info.json' file. The

    @type  root: string
	@param root: The directory path to the corpus.
    """
    self._root = root
    
    # corpus type is specific to Plos_builder
    # full - all documents that were built.
    # partial - documents excluding training 
    # training - documents intended for training
    if 'corpus_type' in kwargs:
      self._corpus_type = kwargs['corpus_type']
      del kwargs['corpus_type']
    else:
      self._corpus_type = 'full'
    
    fn = '{d}/{t}_corpus_info.json'.format(d=root, t=self._corpus_type)
    with open( fn, 'r' ) as fp:
      self._corpus_info = info = json.load(fp)

    # doc_part is specific to PLoS and research article.
	# 'abstract' and 'body' are currently supported.
	# The corpus contains seperate text for each, but the 
	# reader is initialized to read only one.
    if 'doc_part' in kwargs:
      self._doc_part = doc_part = kwargs['doc_part']
      del kwargs['doc_part']
    else:
      self._doc_part = doc_part = 'body'
    
    if 'fileids' not in kwargs:
      fileids = [ doi2fn(d, doc_part) for d in self.dois() ] 
    else:
	    fileids =  kwargs['fileids']
    # cat_map f -> [ c1, c2, ...]
	# The fileids depend on what the doc_part is ('body', 'abstract')
    kwargs['cat_map'] = { doi2fn(d, doc_part) : cat for d,cat in info['dois_to_categories'].iteritems() }
	  # Subclass of Categorized Plaintext Corpus Reader
    CategorizedPlaintextCorpusReader.__init__(self, root, fileids, **kwargs)

  def dois(self):
    """
	  """
    return self._corpus_info['dois_to_categories'].keys()
    
  def article_info(self, doi_lst=None):
    """
    """
    article_info = self._corpus_info['doi_article_info']
    _doi_list = self.dois() if doi_lst == None else doi_lst
    return [ (d, article_info[d]) for d in _doi_list ]

  def article_page_url(self, doi_lst=None):
    """
    """
    article_info = self._corpus_info['doi_article_info']
    page_url = lambda doi : article_info[doi]['page_url']
    _doi_list = self.dois() if doi_lst == None else doi_lst
    return [ (d, page_url(d)) for d in _doi_list ]

  def article_xml_url(self, doi_lst=None):
    """
    """
    article_info = self._corpus_info['doi_article_info']
    xml_url = lambda doi : article_info[doi]['xml_url']
    _doi_lst = self.dois() if doi_lst == None else doi_lst
    return [ (d, xml_url(d)) for d in _doi_lst ]

  def doi_body_fid(self, doi_lst=None):
    """
    """
    article_info = self._corpus_info['doi_article_info']
    body_fid = lambda doi : article_info[doi]['body_fid']
    _doi_lst = self.dois() if doi_lst == None else doi_lst
    return [ (d, body_fid(d)) for d in _doi_lst ]
  
  def doi_abstract_fid(self, doi_lst=None):
    """
    """
    article_info = self._corpus_info['doi_article_info']
    abstract_fid = lambda doi : article_info[doi]['abstract_fid']
    _doi_lst = self.dois() if doi_lst == None else doi_lst
    return [ (d, abstract_fid(d)) for d in _doi_lst ]    

  def author(self, doi_lst=None):
    """
    Build a list of (doi , author) tuples.
	  """
    article_info = self._corpus_info['doi_article_info']
    auth_tuple = lambda doi : tuple(article_info[doi]['author'])
    _doi_lst = self.dois() if doi_lst == None else doi_lst
    return [ (d, auth_tuple(d)) for d in _doi_lst ] 

  def pub_date(self, doi_lst=None):
    """
    """
    article_info = self._corpus_info['doi_article_info']
    pub_date = lambda doi : article_info[doi]['publication_date']
    _doi_lst = self.dois() if doi_lst == None else doi_lst
    return [ (d, pub_date(d)) for d in _doi_lst ]

  def article_type(self, doi_lst=None):
    """
    """
    article_info = self._corpus_info['doi_article_info']
    art_type = lambda doi : article_info[doi]['article_type']
    _doi_lst = self.dois() if doi_lst == None else doi_lst
    return [ (d, art_type(d)) for d in _doi_lst ]

  def title(self, doi_lst=None):
    """
    """
    article_info = self._corpus_info['doi_article_info']
    title = lambda doi : article_info[doi]['title']
    _doi_lst = self.dois() if doi_lst == None else doi_lst
    return [ (d, title(d)) for d in _doi_lst ]

####################### MAIN ##########################

if __name__ == "__main__":
  from docopt import docopt
  args = docopt(__doc__,
                argv=None,
                version='oa_nlp.nltk.plos_reader v.' + __version__,
                options_first=True)
  
  corpus = args['CORPUS_NAME']
  command = args['COMMAND']
  corp_type = args['--corpus-type']
  doc_part = args['--doc-part']
  
  rdr = Plos_reader( corpus, corpus_type=corp_type, doc_part=doc_part )
  cmd_dispatch = {
          'art-info'      : lambda : rdr.article_info(),
          'art-page-url'  : lambda : rdr.article_page_url(),
          'art-xml-url'   : lambda : rdr.article_xml_url(),
          'body-fn'       : lambda : rdr.doi_body_fid(),
          'abst-fn'       : lambda : rdr.doi_abstract_fid(),
        }
        
  if command in cmd_dispatch:
    print(json.dumps(cmd_dispatch[command](), indent=2))
  else:
    print('Unrecognized command "{c}"'.format(c=command))
