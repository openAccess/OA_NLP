from lxml import etree
import cStringIO
import codecs
import csv
import requests
import string
import re
import json
from urllib2 import urlopen, quote
from datetime import datetime, timedelta

SEARCH_URL_TMPL = 'http://api.plos.org/search?{params}'

def search(query='*:*'):
    '''
    Basic Solr search functionality.
    '''
    if isinstance(query,str): 
        query = { 'q' : query }	
    else:
        if not query.has_key('q'): 
            query['q'] = '*:*' #make sure we include a 'q' parameter
    query['wt'] = 'json' #make sure the return type is json
    query['fq'] = quote('doc_type:full AND !article_type_facet:"Issue Image"') #search only for articles
    query['api_key'] = '7Jne3TIPu6DqFCK' 

    params = ['{k}={v}'.format(k=k, v=v) for k,v in query.iteritems()]
    params = string.join(params, '&')
    print ('Request params: ' + params)

    return json.load(urlopen(SEARCH_URL_TMPL.format(params=params)['response']['docs']

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def doGet(url, verify=False):
    """
    Requests for Humans is not so human after all.
    The verfiy parameter fails if the URL is not https:(
    """
    if url.lower().startswith('https:'):
        return requests.get(url, verify=verify)
    else:
        return requests.get(url)

def fetchEntrez(id):
    """
    Fetch the list of article PLOS identifiers 
    for the given Server and Prefix.
    """
    url = ENTREZ_URL_TMPL.format(id=id)
    r = doGet(url)
    if r.status_code == 200:
        # Load JSON into a Python object and use some values from it.
        entrez = etree.fromstring(r.content)
    else:
        raise Exception("Entrez request failed  " + url)
    return entrez

aeInfoMap = {}

with open('out.csv', 'wb') as csvOut:
    writer = UnicodeWriter(csvOut, delimiter=',', quotechar='"')

    with open('NewAEData4.csv', 'rb') as csvIn:
        reader = csv.reader(csvIn, delimiter=';', quotechar='"')
        delThese = "[\.\:;\(\)\,\?\+\\\\/]" 
        for r in reader:
            peopleID = r[0]
            pmid = r[2]
            print("PMID precessing : " + pmid)
            xml = fetchEntrez(pmid)
            abstract = xml.findtext('.//AbstractText')
            if not abstract == None:
                abstract = string.replace(abstract, '\n', ' ')
                abstract = re.sub(delThese, " ", abstract, 0,0)
                title = string.replace(xml.findtext('.//ArticleTitle'),  '\n', ' ')
                title = re.sub(delThese, " ", title, 0,0)
                if not aeInfoMap.has_key(pmid):
                    writer.writerow([peopleID, pmid, title, abstract])
                    aeInfoMap[pmid] = 1
                else:
                    print("PMID : " + pmid + " used more than once")
            else:
                print("PMID : " + pmid + " has no abstract.")
        csvIn.close()
    csvOut.close()
