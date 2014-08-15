#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
oa_nlp.nltk.plos_builder

PLOS solr api. http://api.plos.org/search

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

  -o --out_dir=<dir_name> directory created to for corpus files.
                          [default: new-corpus]

  -v --version            show program version and exit.

  -j --journals=<list>    specify a source journal(s) to search.
                          One or more journal identifiers in a comma
                          separated list. (ex: pone,pbio,pmed,pgen,pcbi,pntd,ppat)
                          [default: *]
  
  -t --train=<n>          build a training corpus in addition to the
                          data corpus. Every n'th document is added to
                          the training corpus instead of the data corpus.
                          A value greater than 0 triggers making a 
                          a training corpus. [default: 0]
                       

Author:
  Bill OConnor

License:
  Apache 2.0

"""
from __future__ import division

import os, re, nltk, json, codecs
from util import doi2fn, field_list_to_dict
from datetime import datetime
from collections import defaultdict
from oa_nlp.plos_api.solr import article_page_url, article_xml_url, Query

__version__ = "0.1"
__all__ = ['Plos_builder',]

# These fields are required for the corpus
QUERY_RTN_FLDS = ('id','journal','publication_date',
                  'article_type','author','subject',
                  'title','abstract','body','editor',
                 )

def _article_info(doc, doi):
  fields = ['journal', 'publication_date', 'article_type', 'title']
  article_info = field_list_to_dict(doc, fields)
  article_info['page_url'] = article_page_url(doi, pretty=True)
  article_info['xml_url'] = article_xml_url(doi, pretty=True)
  return article_info

def _write_doc(base_dir, doc, doi):
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

class Plos_builder(object):
  """
  OA_NLP corpus builder for NLTK compatibility.
  """
  def __init__(self, query, base_dir):
    self.base_dir = base_dir
    self.creation_date = datetime.now().isoformat()
    self.doc_count = 0
    self.query = query
    self.categories_to_dois = defaultdict(list)
    self.dois_to_categories = dict()
    self.doi_article_info = dict()
    return

  def _retain_category_info(self, doc, doi):
    subjs = [] if 'subject' not in doc else doc['subject']
    self.dois_to_categories[doi] = subjs

    # Category -> [ f1, f2, .... ]
    for s in subjs:
      self.categories_to_dois[s].append(doi)
    return

  def build(self, docs):
    """
    Create a json file for each doc returned by the query.
    Then create a corpus info file.

    @type docs: generator 
    @param docs: A list containing the results of a PLoS search query.
                 Each item is a dictionary with QUERY_RTN_FLDS as keys.

    @return: Nothing
    """
    for doc in docs:
      self.add(doc)
    self.finalize()
    return

  def add(self, doc):
    """
    Create a json file for each doc in the document list.

    @type doc: dict
    @param doc: a single document returned with QUERY_RTN_FLDS as keys.

    @return: Nothing
    """
    # Build all the lists and mappings
    doi = doc['id']
    self._retain_category_info(doc, doi)
    self.doi_article_info[doi] =  _article_info(doc, doi) 
    _write_doc(self.base_dir, doc, doi)
    self.doc_count += 1
    return
 
  def finalize(self):
    """
    Save the corpus info file.
    """
    # Dump the info file.
    corpus_info = { 
        'document_count' : self.doc_count,
        'creation_date' : self.creation_date,
        'query' : self.query,
        'categories_to_dois' : self.categories_to_dois,
        'dois_to_categories' : self.dois_to_categories,
        'doi_article_info' : self.doi_article_info
        }
 
    fn = '{d}/corpus_info.json'.format(d=self.base_dir)
    with open(fn, 'w') as fd:
      json.dump(corpus_info, fd, indent=2 )
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

  out_dir='new-corpus' if args['--out_dir'] == None else args['--out_dir']
  os.mkdir(out_dir)

  journal_ids = args['--journals'].split(',')
  queries = args['QUERY']

  queries.append('article_type:"Research Article"')

  pq = Query(api_key, queries, QUERY_RTN_FLDS, journal_ids, limit=limit)
  builder = Plos_builder(queries, out_dir)
  
  train = int(args['--train'])
  if train > 0:
    train_dir = 'train-'+out_dir
    train_builder = Plos_builder(queries, train_dir)
    os.mkdir(train_dir)
 
  count = 0 
  for r in pq:
    print('Processing: {d}'.format(d=r['id']))
    if train > 0 and (count % train) == 0:
      train_builder.add(r)
    else:
      builder.add(r)
    count += 1
  
  if train > 0:
    train_builder.finalize()
  
  builder.finalize()  
  print('{n} articles added to corpus.'.format(n=str(count)))
