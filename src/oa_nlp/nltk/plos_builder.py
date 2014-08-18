#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
oa_nlp.nltk.plos_builder

PLOS solr api. http://api.plos.org/search

  Description:
  ===========

  There are 3 different types of corpora created "full', "partial" and "training". 
  The the "full" corpus includes both the partial and training articles. The 
  "partial" is intended for experimentation. The "training" corpus is a smaller 
  subset of "full" that is not in "partial" that can be used to train classifiers.  
    
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
  replaced by '-' and doc_part is either 'body' or 'abstract'.

Usage:
  plos_builder.py [options] QUERY ...

Examples:
  plos_builder.py --journals=pone,pbio -l 20  "title:('DNA')"

Options:
  -h --help               show this help and exit.

  -a --api-key=<key>      api key [default: 7Jne3TIPu6DqFCK]

  -l --limit=<n>          limit the number of returned records.
                          Set limit to "*" to iterate through
                          the entire returned record set.
                          [default: 99]

  -o --out-dir=<dir_name> directory created to for corpus files.
                          [default: new-corpus]

  -v --version            show program version and exit.

  -j --journals=<list>    specify a source journal(s) to search.
                          One or more journal identifiers in a comma
                          separated list. (ex: pone,pbio,pmed,pgen,pcbi,pntd,ppat)
                          [default: *]

  -d --desc=<str>         short description of corpus.
                          [default: "Based on PLOS main corpus."]
  
  -t --train=<n>          build a training corpus in addition to the
                          data corpus. Every n'th document is added to
                          the training corpus instead of the data corpus.
                          A value greater than 1 triggers making a 
                          a training corpus.
                          [default: 10]

Author:
  Bill OConnor

License:
  Apache 2.0
  
Copyright (c) 2012-2014 OA_NLP Project
"""
from __future__ import division

import os, sys, nltk, json, codecs
from util import doi2fn, field_list_to_dict
from datetime import datetime
from collections import defaultdict, OrderedDict
from oa_nlp.plos_api.solr import article_page_url, article_xml_url, Query

__version__ = "0.1"
__all__ = ['Plos_builder',]

# These fields are required for the corpus
QUERY_RTN_FLDS = ('id','journal','publication_date',
                  'article_type','author','subject',
                  'title','abstract','body','editor',
                 )
class Corpus_info(object):
  """
  Tracks various info related to a corpus.
  """
  def __init__(self, query, base_dir, desc):
    self.creation_date = datetime.now().isoformat()
    self.desc = desc
    self.doc_count = 0
    self.query = query
    self.categories_to_dois = defaultdict(list)
    self.dois_to_categories = dict()
    self.doi_article_info = OrderedDict()
    return

  def _article_info(self, doc, doi):
    fields = ['title', 'author', 
              'editor', 'publication_date', 
              'article_type', 'journal',
              'id' ]
    article_info = field_list_to_dict(doc, fields)
    article_info['page_url'] = article_page_url(doi, pretty=True)
    article_info['xml_url'] = article_xml_url(doi, pretty=True)
    article_info['body_fid'] = doi2fn(doi, 'body')
    article_info['abstract_fid'] = doi2fn(doi, 'abstract')
    return article_info

  def retain_info(self, doc, doi):
    subjs = [] if 'subject' not in doc else doc['subject']
    self.dois_to_categories[doi] = subjs

    # Category -> [ f1, f2, .... ]
    for s in subjs:
      self.categories_to_dois[s].append(doi)

    self.doi_article_info[doi] =  self._article_info(doc, doi)
    self.doc_count += 1
    return

  def finalize(self):
    return OrderedDict( [
        ('desc', self.desc),
        ('document_count',  self.doc_count),
        ('creation_date', self.creation_date),
        ('query', self.query),
        ('categories_to_dois', self.categories_to_dois),
        ('dois_to_categories', self.dois_to_categories),
        ('doi_article_info', self.doi_article_info)
        ] )

class Plos_builder(object):
  """
  OA_NLP corpus builder for NLTK compatibility.
  """
  def __init__(self, query, base_dir, desc, train=0):
    self.base_dir = base_dir
    self.doc_total_count = 0
    self.full_corpus_info = Corpus_info(query, base_dir, desc)
    self.corpus_info = Corpus_info(query, base_dir, desc)
    self.train = train
    self.trainer_info = None if train < 1 else Corpus_info(query, base_dir, desc)
    os.mkdir(base_dir)
    return

  def __enter__(self):
    return self

  def __exit__(self, type, value, traceback):
    self.finalize()

  def _write_doc(self, base_dir, doc, doi):
    """
    Write the abstract and body files.
    """
    fn_body = '{d}/{f}'.format(d=base_dir, f=doi2fn(doi, 'body'))
    fn_abstract = '{d}/{f}'.format(d=base_dir, f=doi2fn(doi, 'abstract'))
    with codecs.open(fn_body, 'w', encoding='utf-8') as fd_body:
      fd_body.write(doc['body'])
    with codecs.open(fn_abstract, 'w', encoding='utf-8') as fd_abstract:
      fd_abstract.write(doc['abstract'][0])
    return
  
  def build(self, docs):
    """
    Create a txt file for each doc returned by the query.
    Then create a corpus info file.

    @type docs: generator 
    @param docs: A list containing the results of a PLoS search query.
                 Each item is a dictionary with QUERY_RTN_FLDS as keys.

    @return: Nothing
    """
    for doc in docs:
      self.add(doc)
    return

  def add(self, doc):
    """
    Create an abstract and body file for each doc in the document list.

    @type doc: dict
    @param doc: a single document returned with QUERY_RTN_FLDS as keys.

    @return: Nothing
    """
    # Build all the lists and mappings
    doi = doc['id']
    self.doc_total_count += 1

    self.full_corpus_info.retain_info(doc, doi)
    if (self.train > 0) and  \
       (self.doc_total_count % train) == 0:
      self.trainer_info.retain_info(doc, doi)
    else:
      self.corpus_info.retain_info(doc, doi)
    
    self._write_doc(self.base_dir, doc, doi)
    return
 
  def finalize(self):
    """
    Save the corpus info files.
    """
    fn = '{d}/full_corpus_info.json'.format(d=self.base_dir)
    with open(fn, 'w') as fd:
      json.dump(self.full_corpus_info.finalize(), fd, indent=2 )

    fn = '{d}/partial_corpus_info.json'.format(d=self.base_dir)
    with open(fn, 'w') as fd:
      json.dump(self.corpus_info.finalize(), fd, indent=2 )

    if not self.trainer_info == None:
      fn = '{d}/training_corpus_info.json'.format(d=self.base_dir)
      with open(fn, 'w') as fd:
        json.dump(self.trainer_info.finalize(), fd, indent=2 )
    return

####################### MAIN ##########################

if __name__ == "__main__":
  from docopt import docopt
  args = docopt(__doc__,
                argv=None,
                version='oa_nlp.nltk.plos_builder v.' + __version__,
                options_first=True)

  api_key = args['--api-key']
  limit = sys.maxint if args['--limit'] == '*' else int(args['--limit'])

  if args['--journals'] == None:
    sys.exit('--journals option must contain one or more journal identifiers.')

  desc = args['--desc'] 
  out_dir='new-corpus' if args['--out-dir'] == None else args['--out-dir']

  journal_ids = args['--journals'].split(',')
  queries = args['QUERY']
  queries.append('article_type:"Research Article"')
  
  train = int(args['--train'])
  if train == 1:
    sys.exit('--train must be greater than 1.')
  
  pq = Query(api_key, queries, QUERY_RTN_FLDS, journal_ids, limit=limit)
  with Plos_builder(queries, out_dir, desc, train=train) as builder:
    for r in pq:
      print('Processing: {d}'.format(d=r['id']))
      builder.add(r)
    print('{n} articles added to corpus.'.format(n=str(builder.doc_total_count)))
