'''
'''
import json

class Reader():

    def __init__(self, corpus_name='myCorpus', path='./', doc_part='body'):
        '''
	corpus_name - the name of the corpus (the directory the files reside in)
        path - the path to the corpus directory (defaults to current directory)
	doc_part - an article can be divided into subparts currently (abstract and body)
        '''
        self.path = path
        self.corpus_name = corpus_name
        self.doc_part = doc_part
        fp = open( path + '/' + corpus_name + '/' + 'corpus_info.json' )
        self.corpus_info = json.load(fp)
        return

    def fileids(self, categories=None):
        '''
	fileids are currently the doi of the article. The '/' is
        converted to a '-' and '.json' suffix added to make the file 
        name.

	categories can be:
	   None - return all the fileids for this corpus
	   type 'str' - make it into a list of one category
	   type 'list' - return the fileids for each category 
                         in the list  
	'''
        if categories == None:
	    return self.corpus_info['fileids'].keys()
        
        # Make single category strings into a list
        cats = [ categories ] if type(categories) == 'str' else categories
        
        # Foreach cat get the fileids. Make a unique list
        # using the keys from a dict.
        fileids = {}
        for cat in cats:
            for fid in self.corpus_info['categories'][cat]:
                fileids[fid] = 1
        return fileids.keys()

    def categories(self, fileids=None):
        '''
        categories are the subjects of the articles. Not all article types have
	subjects. If the article is a Primer, Synopsis, Review etc. the subject
	list will be empty.

	fileids can be:
	    None - return a list of all categories 
	    type 'str' - make inot a list of on fileid
	    type 'list' - returns a list of categories given a 
                          list of fileids 
        '''
	if fileids == None:
	    return self.corpus_info['categories'].keys()

        # Make a single fileid into a list
        fids = [ fileids ] if type(fileids) == 'str' else fileids
        cats = {}
	for fid in fids:
	    # Each fileid has a tuple if info. The 
	    # 4th entry is a list of categories.
            (a,b,c,cl) = self.corpus_info['fileids'][fid]
	    for cat  in cl:
                cats[cat] = 1
        return cats.keys()

    def raw(fileids=None, doc_part='body'):
        
        fids = self.corpus_info['fileids'].keys()  if fileids == None else fileids
        raw_text = ''
        for fid in fids:
            fn = fid.replace('/', '-') + '.json'
	    fd = open( self.path + '/' + self.corpus_name + '/' + fn)
	    article = json.load(fd)
	    raw_text += article[doc_part]
	    fd.close()

	return raw_text

    
    
