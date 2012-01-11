"""
Author: Bill OConnor

"""
import json
from nltk.corpus.reader.plaintext import  CategorizedPlaintextCorpusReader

def _doi2fn(doi, doc_part):
    """
    Convert a DOI to a file name.

    @type doi: string or list
    @param doi: Digital Object Identifier of the article in the corpus.

    @rtype: string or list
    @return: Returns a single file name or a list of filenames..
    """
    fname = lambda d: '%s-%s.txt' % ( d.replace('/', '-'), doc_part)
    if isinstance(doi, basestring): 
        return fname(doi)
    else:
        return [ fname(d) for d in doi ]

def _listafy(obj, aDict):
    """
    """
    if obj == None:
        return aDict.keys()
    elif isinstance(obj, basestring):
        return [ obj ]
    else:
        return obj

class PlosReader(CategorizedPlaintextCorpusReader):
    """
    PlosReader is loosely modeled on ntlk.corpus.api.CategorizedCorpusReader.
    A corpus is generated iby the mkcorpus tool which uses a Solr query to select 
    documents. Meta-data related to the corpus is contained in corpus_info.json.  
    
    In a sense there is no such thing as a definative PLoS corpus. A corpus can
    be created based on a set of selection criteria submitted to the Solr search
    server. The document doi, journal, authors, subjects, publication date, body, 
    abstract and URL to the original artilce XML are included in the meta-data. 
    The PlosReader provides access to this info as well as some standard methods 
    in nltk.readers.

    """
    def __init__(self, root, **kwargs):
        """
	Initialize a PLoS reader with a specific corpus. Corpus 
	information is contained in 'root/corpus_info.json' file. The

        @type  root: string
	@param root: The directory path to the corpus directory.
        """
        self._root = root
        fp = open( '%s/corpus_info.json' % (root), 'r' )
        self._corpus_info = info = json.load(fp)
        fp.close()

        # doc_part is specific to PLoS and articles in general.
	# 'abstract' and 'body' are currently supported.
	# The corpus contains seperate text for each so the 
	# reader is initialized to read one or the other.
        doc_part = kwargs['doc_part']  if 'doc_part' in kwargs else 'body'
        self._doc_part = doc_part
        fileids = [ _doi2fn(d, doc_part) for d in info['d2c'].keys() ] if 'fileids' not in kwargs else kwargs['fileids']

        # cat_map f -> [ c1, c2, ...]
	# The fileids depend on what the doc_part is ('body', 'abstract')
	cat_map = {}
        for d,cat in info['d2c'].iteritems():
            cat_map[_doi2fn(d, doc_part)] = cat

	kwargs['cat_map'] = cat_map
	# Subclass of Categorized Plaintext Corpus Reader
        CategorizedPlaintextCorpusReader.__init__(self, root, fileids, **kwargs)

    def articleURL(self, doi_lst=None):
        """
        """
	dois = _listafy(doi_lst, self.corpus_info['d2c'])
	amap = self._corpus_info['article_link']
        return zip(dois, [ amap[d] for d in dois])

    def articleXML(self, doi_lst=None):
        """
        """
	dois = _listafy(doi_lst, self._corpus_info['d2c'])
	xmap = self._corpus_info['xml_link']
        return zip(dois, [ xmap[d] for d in dois ])

    def doi2fid(self, doi_lst=None):
        """
        """
        dois = _listafy(doi_lst, self._corpus_info['d2c']) 
        return zip(dois, _doi2fn(dois, self._doc_part))

    def authors(self, doi_lst=None):
        """
        Build a list of (doi , author) tuples.
	"""
        dois = _listafy(doi_lst, self._corpus_info['d2c'])
	d2info = self._corpus_info['d2info']
	alist = []
	for d in dois:
            (_,_,_,_,authors) = d2info[d]
	    alist.extend([ (d, a) for a in authors])
        return alist

    def pub_date(self, doi_lst=None):
        """
        """
        dois = _listafy(doi_lst, self._corpus_info['d2c'])
	d2info = self._corpus_info['d2info']
	dlist = []
	for d in dois:
            (_,pd,_,_,_) = d2info[d]
	    dlist.extend((d, pd))
        return dlist

    def article_type(self, doi_lst=None):
        """
        """
        dois = _listafy(doi_lst, self._corpus_info['d2c'])
	d2info = self._corpus_info['d2info']
	alist = []
	for d in dois:
            (_,_,atype,_,_) = d2info[d]
	    alist.extend((d, atype))
        return alist

    def title(self, doi_lst=None):
        """
        """
        dois = _listafy(doi_lst, self._corpus_info['d2c'])
	d2info = self._corpus_info['d2info']
	tlist = []
	for d in dois:
            (_,_,_,t,_) = d2info[d]
	    tlist.extend((d, t))
        return tlist
