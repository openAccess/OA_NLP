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
    fname = lambda d: '{i}-{p}.txt'.format(i=d.replace('/', '-'),p=doc_part)
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

def field_list_to_dict(dict_, keys):
  """
  Some fields might not exist - need '' in the key.

  @type dict_: dict
  @param dict_: dictionary to extract values for specified keys from.
  @type keys: list
  @param keys: list of keys used to extract from the provided dictionary.

  @rtype: dict
  @return: returns a dictionary containing the data extracted from dict_.
  """
  assign_if = lambda f, d : d[f] if f in d else ''
  return { key : assign_if(key,dict_) for key in keys}
