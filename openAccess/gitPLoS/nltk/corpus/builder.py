'''
'''
import re
_defaultStopWords = ('', 'a', 'is', 'it','to', 'by', 'be', 
                     'then', 'the', 'for', 'of', 'and', 
                     'with', 'fig', 'i.e', 'e.g', 'in', 'we',
		     'have', 'as', 'an', 'its', 'but', 'also',
		     'at', 'so')

ReturnFields = 'id,journal,author,subject,abstract,body'

def _wsTokenize( s ):
    return s.split()

def _toLower ( l ):
    return [ w.lower() for w in l]

def _rmBlanks( l ):
    return [ w for w in l if w is not '']

def _count( l ):
    counts = {}
    for w in l:
        counts[w] = counts[w] + 1 if w in counts else 1
    return counts

def _rmTrailingPunc( l ):
	return [ w.rstrip(' -,;?.:)(').lstrip(' -,;?.:)(') for w in l]

def _rmRefNums( l ):
    pat = re.compile(r'''\[\d+\]''')
    return [ w for w in l if not pat.match(w)]

def _rmStopWords( stop_words, l ):
    return [ w for w in l if w not in stop_words]

class Builder():

    def __init__(self, stop_words = _defaultStopWords) :
        self.stop_words = stop_words
        return

    def build(self, doc):
	wl = _wsTokenize(doc['abstract'][0])
	wl = _toLower( wl )
	wl = _rmBlanks( wl )
	wl = _rmTrailingPunc( wl )
	doc['abstract_wl'] = _rmStopWords( self.stop_words, wl )
	doc['abstract_cnt'] = _count( doc['abstract_wl'] )

	wl = _wsTokenize(doc['body'])
	wl = _toLower( wl )
	wl = _rmTrailingPunc( wl )
	wl = _rmRefNums( wl )
	wl = _rmBlanks( wl )
	doc['body_wl']  = _rmStopWords( self.stop_words, wl )
	doc['body_cnt'] = _count( doc['body_wl'] )
	return doc

    
