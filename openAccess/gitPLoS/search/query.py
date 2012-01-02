#! /usr/bin/env python
'''
   Author: Bill OConnor 
   Description: Command line tools for PLoS search API

   The Public Library of Science (PLoS) publishes peer 
   reviewed research under the Creative Commons license. 
   All articles are available to the public free of charge. 
   Info regarding the RESTful web API to the PLoS Solr based 
   search engine is available at http://api.plos.org. 
   
   This is a collection of python modules and commandline 
   tools to aid in using this api. 

   License: http://www.opensource.org/licenses/mit-license.php

'''
import json
from urllib2  import urlopen, quote, unquote
	
__version__ = "0.1"
__all__ = ['articleUrl', 'articleXML', 'PlosSearch']

_searchUrl = 'http://api.plos.org/search?'
'''
   _JMap - map a journal name to a url.
'''
_JMap = {
		'PLoS Biology'               : 'http://www.plosbiology.org',
		'PLoS Genetics'              : 'http://www.plosgenetics.org',
		'PLoS Computational Biology' : 'http://www.ploscompbiol.org',
		'PLoS Medicine'              : 'http://www.plosmedicine.org',
		'PLoS ONE'                   : 'http://www.plosone.org',
		'PLoS Neglected Tropical Diseases' : 'http://www.plosntds.org',
		'PLoS Clinical Trials'       : 'http://clinicaltrials.ploshubs.org',
		'PLoS Pathogens'             : 'http://www.plospathogens.org'
	    }
'''
   _JIds - map a 4 character journal id to quoted journal name.
'''
_JIds = {
		'pbio' : '"PLoS Biology"',
		'pgen' : '"PLoS Genetics"',
		'pcbi' : '"PLoS Computational Biology"',
		'pmed' : '"PLoS Medicine"',
		'pone' : '"PLoS ONE"',
		'pntd' : '"PLoS Neglected Tropical Diseases"',
		'pctr' : '"PLoS Clinical Trials"',
		'ppat' : '"PLoS Pathogens"'
	}	

def articleUrl(doi,jid):
    '''
    articleUrl- return a valid link to the article page given the journal
                4 character identifier and the article doi.
    '''
    return _JMap[jid] + '/article/' + quote('info:doi/' + doi)

def articleXML(doi,jid):
    '''
    articleXML - return a valid link to the article XML give the journal
                 4 character identifier and the article doi.
    '''
    return _JMap[jid] + '/article/fetchObjectAttachment.action?uri=' + quote('info:doi/' + doi) +\
                        '&representation=XML'
 
def mkQueryUrl(url, query):
    '''	
    mkQuery - given a url and a dictionary of parameters keys and values
              create a valid url query string.
    '''
    paramList = [ '%s=%s' % (k, quote(v)) for k,v in query.iteritems()]
    return url + "&".join(paramList) 

def mkJrnlQuery(jrnls):
    return 'journal:(' + ' OR '.join( [_JIds[j] for j in jrnls] ) + ')'

class Query:
    '''
        PlosQuery - provides basic framework to access PLoS http://api.plos.org.       
    '''
    def __init__(self, api_key, start=0, limit=99, maxRows=50, verbose=False):
        self.start = start; self.limit = limit; self.api_key = api_key
        self.verbose = verbose; self.cursor = -1
        self.maxRows = limit if limit < maxRows else maxRows
        self.qmap = {
		    'start': str(self.start),
                    'rows': str(self.maxRows),
                    'fq': 'doc_type:full AND !article_type_facet:"Issue Image"',
                    'wt': 'json',
                    'api_key': api_key,
                   } 
        self.docs = []; self.status = -1; self.QTime = -1; self.numFound = 0
                
    # Iterator Protocol       
    def __iter__(self):
        return self
       
    def next(self):
        self.cursor += 1
        if self.cursor == len(self.docs):
            self.start += self.cursor
            rows = self.maxRows
            if (self.start >= self.limit) or (self.start >= self.numFound):
                raise StopIteration

            if (self.start + self.maxRows) > self.limit:
               rows = self.limit - self.start
            
            self.cursor = 0
            self.qmap['start'] = str(self.start)
            self.qmap['rows'] = str(rows)
            self.query(None, None, iterate=True)

        return self.docs[self.cursor]

    def __getitem__(self):
        return self.docs[self.cursor]
                         
    def _doQuery(self, query):
        '''
        '''
        url = mkQueryUrl(_searchUrl, query )
        j = json.load(urlopen(url))
        return (j['responseHeader'],j['response'], url)
	
    def query(self, args, fields, iterate=False):
        '''
	search - returns a list of documents. 
	    args   - a list of strings specifying the query to preform.
			    
	    fields - return fields to be included in the search results.
		    
	    iterate - if iterate is true skip building a new query and
	              re-submit the request. Only used when the row limit
		      is larger than maxRows.
	'''
	# If we are iterating skip the assembling the query.
        if not iterate:
            if len(args) > 0:
                self.qmap['q'] = ' AND '.join(args)    
            self.qmap['fl'] = fields 

        (header, resp, url) = self._doQuery(self.qmap)
        self.status = header['status']; self.QTime = header['QTime']
        self.numFound = resp['numFound']
        self.docs = resp['docs']
                
        if self.verbose: 
            print 'Query url: ' + unquote(url) 
            print 'Status: %s\nQTIme: %s\nStart: %s\nnumFound: %s\n' % \
              (self.status, self.QTime, self.start, self.numFound)
            print json.dumps(self.docs, indent=5)

        return self.docs
	
if __name__ == "__main__":
    # Commandline parser setup
    from optparse import OptionParser
    usage = "usage: %prog [optionS] query1 query2 ..."
    parser = OptionParser(usage=usage)
	
    parser.add_option('-j', '--journal', 
                      action='store', dest='jrnl', default=None,
                      help='Default journal is "all". One of more journals can be specified ' + \
                      'comma separated identifier list. [pone,pbio,pmed,pgen,pcbi,pntd,ppat].' )
    parser.add_option('-l', '--limit', 
		      action='store', dest='limit', type='int', default=99,
                      help='Maximum number of documents to return. default=99' )
    parser.add_option("-v", "--verbose", 
                      action='store_true', dest='verbose', default=False,
                      help='Verbose mode for debugging.' ) 
    parser.add_option('-a', '--api-key',
		      action='store', dest='api_key', default='7Jne3TIPu6DqFCK',
		      help='API key obtained from PLoS.' ) 
    parser.add_option('-f', '--fields', 
                      action='store', type='string', dest='fields', default='id,title,author',
                      help='Fields to return in query. Fields are comma seperated' + 
                      ' with no spaces. default=id,title,author\n' +
                      '[id,journal,title,body,author,abstract,subject]' ) 
	
    (opts, args) = parser.parse_args()
	
    # Parse the journal options and add them to the query
    # Journal name are logically OR'd 
    if opts.jrnl is not None:
        args.append(mkJrnlQuery(opts.jrnl.split(',')))
    
    # if no argument specified, wildcard search '*:*'
    if len(args) == 0:
        args = args + ['*:*']

    pq = Query( api_key=opts.api_key, limit=opts.limit, verbose=opts.verbose )
    pq.query(args, opts.fields)
    fields = opts.fields.split(',')
    count = 0
    for r in pq:
        print 'Rec#%d' % (count)
	for f in fields:
            print u'%s:  %s\n' % (f, r.get(f))
        count += 1
