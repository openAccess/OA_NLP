"""
Author: Bill OConnor

"""
import json
from util import doi2fn, listafy, DFLT_DOC_PART
from nltk import word_tokenize, sent_tokenize

class PlosReader(object):
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
    def __init__(self, root='./', name='myCorpus'):
        """
	Initialize a PLoS reader with a specific corpus. Corpus 
	information is contained in 'root/corpus_info.json' file. The

        @type  root: string
	@param root: The directory path to the corpus directory.
	@type  name: string
	@param name: The corpus name/directory. A PLoS corpus is 
	             a directory of article files stored in JSON format.
	@rtype:  PlosReader
	@return: An initialized Plos reader object  
        """
        self.root = root
        self.name = name
        fp = open( '%s/%s/corpus_info.json' % (root, name), 'r' )
        self.corpus_info = json.load(fp)
        fp.close()
        return

    def corpus_info(self):
	"""
	"""
        return self.corpus_info

    def articleURL(self, fileids=None):
        """
        """
	fids = listafy(fileids, self.corpus_info['f2c'])
	amap = self.corpus_info['article_link']
	return [ amap[f] for f in fids]

    def articleXML(self, fileids=None):
        """
        """
	fids = listafy(fileids, self.corpus_info['f2c'])
	xmap = self.corpus_info['xml_link']
        return [ xmap[f] for f in fids ]

    def fileids(self, categories=None):
        """
	File ids (fileids) are not the file names of the article but the
	Digital Object Identifier (DOI). doi2fn converts the doi to a file
	name.

        @type categories: None or string or list
	@param categories: a list of article categories 
	@rtype: list
	@return: The list of article fileids that repesent articles from
	         the list of categories.
	"""
        # Return all fileids if categories == None
        if categories == None: return self.corpus_info['f2c'].keys()
        
        # Make single category strings into a list
        cats = [ categories ] if isinstance(categories, basestring) else categories
        # Foreach cat get the fileids. Make a unique list
        flist = []
        c2fmap = self.corpus_info['c2f']
        for c in c2fmap:
            flist.extend( c2fmap[c] )
        # Return a list of unique ids
        return [ f for f in set(flist) ]

    def categories(self, fileids=None):
        """
        Categories are the subjects of the articles. Not all article types have
	subjects. If the article is a Primer, Synopsis, Review etc. the subject
	list will be empty.
        
	@type fileids: None or string or list
        @param fileids: The file ids 
	@rtype: list
	@return: list of unique categories associated with the fileids.
	"""
	# Return all categories if fileid == None
	if fileids == None: return self.corpus_info['c2f'].keys()

        # Make a single fileid into a list
        fids = [ fileids ] if isinstance(fileids, basestring) else fileids
	# Build a unique list of categories for each fileid
	clist =[]
        f2cmap = self.corpus_info['f2c']
	for doi in f2cmap:
            clist.extend(fmap[fid])
        # Return a list of unique categories
        return [ c for c in set(clist) ]

    def authors(self, fileids=None):
        """
        Build a list of authors of the articles specified by fileids.

	@type fileids: None or string or list
	@param fileids: The file identifiers for each article in the corpus (DOI).
	                None returns all the file ids.
	@rtype: list
	@return: The list of authors of the specified articles.
	"""
        fids = listafy(fileids, self.corpus_info['f2c'])
     
	alist = []
	fnames = [ '%s/%s/%s' % (self.root, self.name, fn) for fn in doi2fn(fids) ] 
	for fn in fnames:
	    fd = open( fn, 'r' )
	    alist.extend(json.load(fd)['author'])
            fd.close()
	return [ a for a in set(alist) ]

    def raw(self, fileids=None, doc_part=DFLT_DOC_PART):
        """
        Return the requested document part as a single string.
	If there are multiple fileids then raw text from multiple
	articles is concatenated into a single string.

	@type fileids: None or string or list
	@param fileids: The file identifiers for each article in the corpus (DOI).
	                None returns all the file ids.
	@type  doc_part: string
	@param doc_part: the article part i.e. 'body', 'abstract'
	@rtype: string
	@return: The concatenated raw text of articles specified in the fileids list.
	"""
        fids = listafy(fileids, self.corpus_info['f2c'])
     
	raw_text = ''
	fnames = [ '%s/%s/%s' % (self.root, self.name, fn) for fn in doi2fn(fids) ] 
	for fn in fnames:
	    fd = open( fn, 'r' )
	    doc = json.load(fd)
	    if doc_part in doc:
                # Abstracts come in a list - if doc_part is a list use the first entry
		part = doc[doc_part] if isinstance(doc[doc_part], basestring) else doc[doc_part][0]
                raw_text += part 
            fd.close()
	return raw_text

    def words(self, fileids=None, doc_part=DFLT_DOC_PART):
        """
        Tokenizes the raw text of the fileids specified using the 
        default word_tokenizer in nltk.
	"""
        return word_tokenize(self.raw(fileids=fileids, doc_part=doc_part))
    
    def sents(self, fileids=None, doc_part=DFLT_DOC_PART):
        """
	Tokenizes the raw text of the fileids specified using the
	default sents_tokenizer in nltk.
        """
        return sent_tokenize(self.raw(fileids=fileids, doc_part=doc_part))
