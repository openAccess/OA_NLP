"""
Author: Bill OConnor

"""

DFLT_DOC_PART = 'body'

def doi2fn(doi):
    """
    Convert a DOI to a file name.

    @type doi: string or list
    @param doi: Digital Object Identifier of the article in the corpus.

    @rtype: string or list
    @return: Returns a single file name or a list of filenames..
    """
    fname = lambda d: '%s.json' % ( d.replace('/', '-'))
    if isinstance(doi, basestring): 
        return fname(doi)
    else:
        return [ fname(d) for d in doi ]

def listafy(obj, aDict):
    """

    """
    if obj == None:
        return aDict.keys()
    elif isinstance(obj, basestring):
        return [ obj ]
    else:
        return obj
