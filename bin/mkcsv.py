#! /usr/bin/env python
#
# Author: Bill OConnor 
# Copyright 2011-2012 Bill OConnor and openAccess project.
# License: See LICENSE.txt 
#

"""
   Description: 
   ============
   
   Command line tools for PLoS search API

   The Public Library of Science (PLoS) publishes peer 
   reviewed research under the Creative Commons license. 
   All articles are available to the public free of charge. 
   Info regarding the RESTful web API to the PLoS Solr based 
   search engine is available at http://api.plos.org. 
   
   This is a collection of python modules and commandline 
   tools to aid in using this api. 

"""
# Commandline parser gitPLoS.search.query
import csv
import cStringIO
import codecs
import string
import re

from optparse import OptionParser 
from gitPLoS.search.query import Query, mkJrnlQuery


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

usage = "usage: %prog [optionS] file"
parser = OptionParser(usage=usage)

parser.add_option('-n', '--name', action='store', dest='name', default='out.csv',
		 help='Name of corpus. Default is "out.csv". Creates a directory ' +
		 'and puts all files related to the corpus there.')

parser.add_option("-v", "--verbose", 
                 action='store_true', dest='verbose', default=False,
                 help='Verbose mode for debugging.' ) 

parser.add_option('-a', '--api-key',
                 action='store', dest='api_key', default='7Jne3TIPu6DqFCK',
                 help='API key obtained from PLoS.' ) 

(opts, args) = parser.parse_args()

with open(args.pop(0), 'rb') as csvIn:
    reader = csv.reader(csvIn, delimiter=',', quotechar='"')
    with open('out.csv', 'wb') as csvOut:
        writer = UnicodeWriter(csvOut)
        delThese = "[\.\:;\(\)\,\?\+\\\\/]"
        for row in reader:
            peopleID = row[0]
            doi = row[1]
            print('Processing : ' + doi)
            q = ['id:"{doi}"'.format(doi=doi)]
            plos_q = Query( api_key=opts.api_key, limit=2 )
            try:
                plos_q.query(q, ','.join(['title','abstract']))

                if opts.verbose:
                    print "%s docs returned." % plos_q.numFound
                #Add each result to the builder
                for d in plos_q:
                    abstract = string.replace(d.get('abstract')[0], '\n', ' ').strip()
                    abstract = re.sub(delThese, " ", abstract, 0,0)
                    title = string.replace(d.get('title'),  '\n', ' ').strip()
                    title = re.sub(delThese, " ", title, 0,0)
                    writer.writerow([peopleID, doi, title, abstract])
            except:
                print('Exception: ' + sys.exc_info()[0])
                print('*' + peopleID + ',' + doi)
        csvIn.close()
        csvOut.close()
    
