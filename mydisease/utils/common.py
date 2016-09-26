from collections import defaultdict
from itertools import chain


def list2dict(xlist, sep=":"):
    """
    Convert list of identifiers to a dict, where the key is everything before the first `sep`

    >>> list2dict(['OMIM:1234','OMIM:1234','OMIM:1111','MESH:C009876','GREG:666','SHITTYID:2134:324','malformed_id'])
    {'MESH': ['C009876'], 'SHITTYID': ['2134:324'], 'OMIM': ['1234', '1234', '1111'], None: ['malformed_id'], 'GREG': ['666']}

    :param xlist:
    :param sep:
    :return:
    """
    d = defaultdict(list)
    for item in xlist:
        if sep not in item:
            key, value = None, item
        else:
            key, value = item.split(sep, 1)
        d[key].append(value)
    return dict(d)


def dict2list(d, sep=":"):
    """
    Convert dict of identifiers to a list, where the key is the ID prefix. Joined using `sep`
    Order of returned list is not specified

    >>> dict2list({'MESH': ['C009876'], 'SHITTYID': ['2134:324'], 'OMIM': ['1234', '1234', '1111'], None: ['malformed_id'], 'GREG': ['666']})
    ['OMIM:1234','OMIM:1234','OMIM:1111','MESH:C009876','GREG:666','SHITTYID:2134:324','malformed_id']

    :param d:
    :param sep:
    :return:
    """
    return list(chain(*[[sep.join([k, vv]) if k else vv for vv in v] for k, v in d.items()]))
