'''
'''
import re
'''
    These are default stop words. Selected by looking at
    corpus results. Probably should turn this into a hash
    for speed.
'''
_defaultStopWords = ('', '=', 
                     'a', 'an', 'as', 'at', 'are','also', 'and', 
                     'be', 'by', 'but',
		     'can', 'could', "can't", 
		     'do', 'did', 'done',
		     'e.g', 'eq',
		     'for', 'fig', 'from',
		     'go', 'gone', 'get',
		     'has', 'had', 'have',
		     'i.e', 'in', 'is', 'it', 'its', 'into',
		     'my', 'mine', 'may', 'maynot',
		     'no', 'not', 
		     'of', 'on', 'or',
                     'to', 'than', 'then', 'the', 'this',
		     'so', 'soon',
                     'we', 'went', 'with', 'within', 'when', 'where', 'were', 'would',
		     "wouldn't",
		    )

# These fields are required for the corpus
ReturnFields = 'id,journal,author,subject,abstract,body'

def _wsTokenize( s ):
    '''
    Split on whitespace and remove blanks.
    '''
    l = s.split()
    return [ t.lower() for t in l if t is not '']

def _count( l ):
    '''
    Make a count of unique words.
    '''
    counts = {}
    for w in l:
        counts[w] = counts[w] + 1 if w in counts else 1
    return counts

def _rmPunc( l ):
    '''
    Some of the words begin or end with punctuatuion.
    '''
    return [ w.rstrip(' -,;?.:)(').lstrip(' -,;?.:)(') for w in l]

def _rmRefNums( l ):
    '''
    Article body has many references of the form [d].
    '''
    pat = re.compile(r'''\[\d+\]''')
    return [ w for w in l if not pat.match(w)]

def _rmStopWords( stop_words, l ):
    '''
    Remove words from the stop word list.
    '''
    return [ w for w in l if w not in stop_words]

class Builder():

    def __init__(self, stop_words = _defaultStopWords) :
        self.stop_words = stop_words
        return

    def build(self, doc):
	wl = _wsTokenize(doc['abstract'][0])
	wl = _rmPunc( wl )
	doc['abstract_wl'] = _rmStopWords( self.stop_words, wl )
	doc['abstract_cnt'] = _count( doc['abstract_wl'] )

	wl = _wsTokenize(doc['body'])
	wl = _rmPunc( wl )
	wl = _rmRefNums( wl )
	doc['body_wl']  = _rmStopWords( self.stop_words, wl )
	doc['body_cnt'] = _count( doc['body_wl'] )
	return doc

    
