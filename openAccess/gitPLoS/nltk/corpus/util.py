"""
Author: Bill OConnor

"""

def doi2fn(doi, doc_part):
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

def listafy(obj, aDict):
    """

    """
    if obj == None:
        return aDict.keys()
    elif isinstance(obj, basestring):
        return [ obj ]
    else:
        return obj
