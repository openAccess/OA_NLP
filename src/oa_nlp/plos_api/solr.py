#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
plos_api solr  

Make queries against the PLOS solr api. http://api.plos.org/search

Usage:
  solr.py [options] QUERY ...
  
Examples:
  solr.py --journals=pone,pbio -l 20 --fields=title,abstract "title:('DNA' AND 'Mitochondria')" 
  
Options:
  -h --help               show this help and exit.
  
  -a --api-key=<key>      api key [default: 7Jne3TIPu6DqFCK]
  
  -l --limit=<n>          limit the number of returned records. 
                          Set limit to "*" to iterate through 
                          the entire returned record set.
                          [default: 99] 
                          
  -v --version            show program version and exit.
  
  -f --fields=<list>      list of fields to return in search results.
                          Fields can be specified is a comma separated
                          list.(ex: id,journal,title,body,author,abstract,subject) 
                          [default: id,title,author]
                          
  -j --journals=<list>    specify a source journal(s) to search. 
                          One or more journal identifiers in a comma 
                          separated list. (ex: pone,pbio,pmed,pgen,pcbi,pntd,ppat)
                          [default: *]
  
  -r --research_only      return research articles only. Same as specifying 
                          'article_type:"Research Article"' as part of the query.
Author:
  Bill OConnor
  
License:
  Apache 2.0
    
"""
import os
import sys
import json
import requests
from urllib2 import quote, unquote
	
__version__ = "0.1"
__all__ = ['article_page_url', 'article_xml_url', 'Query', 'mkJrnlQuery']

_search_url = 'http://api.plos.org/search'
_logger = None

"""
   _id_2_journal - map a 4 character journal id to quoted journal name
                and url tuple.
"""
_id_2_journal= {
  'pbio' : ('"PLoS Biology"', 'http://www.plosbiology.org'),
  'pgen' : ('"PLoS Genetics"', 'http://www.plosgenetics.org'),
  'pcbi' : ('"PLoS Computational Biology"', 'http://www.ploscompbiol.org'),
  'pmed' : ('"PLoS Medicine"', 'http://www.plosmedicine.org'),
  'pone' : ('"PLoS ONE"', 'http://www.plosone.org'),
  'pntd' : ('"PLoS Neglected Tropical Diseases"', 'http://www.plosntds.org'),
  'pctr' : ('"PLoS Clinical Trials"', 'http://clinicaltrials.ploshubs.org'),
  'ppat' : ('"PLoS Pathogens"', 'http://www.plospathogens.org'),
  }	
  
def _do_get(url):
  """
  Requests for Humans not so human after all.
  The verify parameter fails if the URL is not https:(
  """
  if url.lower().startswith('https:'):
    return requests.get(url, verify=False)
  else:
    return requests.get(url)
    
def _do_query(query_map):
  url = _build_solr_url(_search_url, query_map)
  r = _do_get(url)
  if r.status_code == 200:
    # Load JSON into a Python object and use some values from it.
    json_rslt = json.loads(r.content)
  else:
    raise Exception('_do_query: failed ' + url)
  return (json_rslt['response'], url)
  
def _build_query_map(api_key, start, rows, query='', fields=''):
  qmap = {
    'start': str(start),
    'rows':  str(rows),
    'fq': 'doc_type:full AND !article_type_facet:"Issue Image"',
    'wt': 'json',
    'api_key': api_key,
    'q' : query,
    'fl' : ','.join(fields),
  }
  return qmap
  
def _set_query_map(qmap, start, rows):
  qmap['start'] = str(start)
  qmap['rows'] = str(rows)
  return qmap
  
def _journal_id(doi):
  _,_,jid,_ = doi.split('.')
  return jid
  
def _journal_url(doi):
  _,url = _id_2_journal[_journal_id(doi)]
  return url
 
def _build_solr_url(url, query):
  """	
  _build_solr_url - given a url and a dictionary of parameter keys and values
                    create a valid url query string.
  """
  params = [ '{k}={v}'.format(k=k, v=quote(v)) for k,v in query.iteritems() ] 
  return '{url}?{params}'.format(url=url, params="&".join(params)) 

def _jrnl_query_params_str(journal_ids):
  """
  _jrnl_query_str - given a list of journal id's form a disjunctive search parameter 
               string for journal names.
  """
  journal_names = [ n for n,u in [_id_2_journal[i] for i in journal_ids] ] 
  return 'journal:( {jnames} )'.format(jnames=' OR '.join(journal_names))

def _build_conjunctive_query_str(queries=['*:*'], journal_ids=['*']):
  """
  _build_conjuntive_query_str - build a conjunctive query 
  """
  new_query_str = [ q for q in queries ]
  if not journal_ids[0] == '*':
    journal_str = _jrnl_query_params_str(journal_ids)
    new_query_str.append(journal_str)
    
  return ' AND '.join(new_query_str)
  
def article_page_url(doi, pretty=False):
  """
  article_page_url- return a valid link to the article page given 
                    the plos article doi.
  """
  url = _journal_url(doi)
  _doi = 'info:doi/'+ doi
  _doi = quote(_doi) if not pretty else _doi
  return '{url}/article/{doi}'.format(url=url, doi=_doi)

def article_xml_url(doi, pretty=False):
  """
  article_xml_url - return a valid link to the article XML give the journal
                    the article doi.
  """
  url = _journal_url(doi) 
  _doi = 'info:doi/'+ doi
  _doi = quote(_doi) if not pretty else _doi 
  return '{url}/article/fetchObjectAttachment.action?representation=XML'\
         '&uri={doi}'.format(url=url, doi=_doi)
    
class Query(object):
  """
  Iterable PLOS Solr query object.     
  """
  def __init__(self, api_key, queries, return_fields, journals,
                     start=0, limit=99, chunk_size=400          ):
    self.start = start; 
    self.limit = limit; 
    self.chunk_size = limit if limit < chunk_size else chunk_size
    self.cursor = 0
    self.buffer_cursor = 0
    self.qmap = _build_query_map(api_key, self.start, self.chunk_size, 
                                 _build_conjunctive_query_str(queries, journals),
                                 return_fields)       
    self.buffer = []; 
    self.numFound = 0; self.num_returned = 0
    
  def _fetch_docs(self, start, rows):
    _set_query_map(self.qmap, start, rows)
    (resp, url) = _do_query(self.qmap)
    self.numFound = int(resp['numFound'])
    if self.numFound < self.limit:
      self.limit = self.numFound
    self.buffer = resp['docs']
    self.num_returned = len(self.buffer)
    return
                
  # Iterator Protocol       
  def __iter__(self):
    self.cursor = self.start
    self.buffer_cursor = 0
    self.buffer = []
    self._fetch_docs(self.cursor, self.chunk_size)   
    return self

  # Iterator Next    
  def next(self):
    if self.cursor == self.limit:
      raise StopIteration

    if self.buffer_cursor == self.chunk_size:
      self.buffer_cursor = 0
      self._fetch_docs(self.cursor, self.chunk_size)

      if self.num_returned == 0:
        raise StopIteration

    doc = self.buffer[self.buffer_cursor]   
    self.buffer_cursor += 1 
    self.cursor += 1  

    return doc

####################### MAIN ##########################

if __name__ == "__main__":
  from docopt import docopt  
  args = docopt(__doc__,
                argv=None,
                version='plos_api.solr v.' + __version__,
                options_first=True)
                
  api_key = args['--api-key']
  limit = sys.maxint if args['--limit'] == '*' else int(args['--limit'])

  if args['--fields'] == None:
    sys.exit('--fields option must contain one or more field identifiers.')
  
  field_ids = args['--fields'].split(',')
  
  if args['--journals'] == None:
    sys.exit('--journals option must contain one or more journal identifiers.')
    
  journal_ids = args['--journals'].split(',')  
  queries = args['QUERY']

  if args['--research_only']:
    queries.append('article_type:"Research Article"')
 
  pq = Query(api_key, queries, field_ids, journal_ids, limit=limit)
  count = 1
  for r in pq:
    json_dict = dict()
    json_dict['{c}'.format(c=str(count))] = { f : r.get(f) for f in field_ids }
    print(json.dumps(json_dict, indent=5))
    count += 1
