import collections
from pprint import pprint
from typing import List


def merge_type_dict(dl):
    """
    Input: list of dictionaries. keys are anything, values are types

    Return: aggregate of list, checking to make sure the types are consistent between all members

    Examples
    --------
    >>> dl = [{'a':str},{'a':str,'b':int},{'a':str}]
    >>> merge_type_dict(dl)
    {'a': str, 'b': int}

    >>> dl = [{'a':str},{'a':str,'b':int},{'a':int}]
    >>> merge_type_dict(dl)
    Traceback (most recent call last):
    ...
    AssertionError: inconsistent types <class 'int'> and <class 'str'> in a

    """
    d = {}
    for x in dl:
        for k, v in x.items():
            if k in d:
                assert mapping_list_equal(v, d[k]), "inconsistent types {} and {} in {}".format(v, d[k], k)
        d.update(x)
    return d


def mapping_list_equal(a,b):
    """
    If a and b are of type typing.List, compare if they are equal accounting for unspecified types
    (arising from an empty list)
    Otherwise return `a==b`
    """

    if not len({hasattr(a, "__args__"), hasattr(b, "__args__")}) == 1:
        return False
    if hasattr(a, "__args__"):
        if a.__args__ is None and b.__args__ is None:
            return True
        if a.__args__ is None or b.__args__ is None:
            return True
        else:
            return a == b
    else:
        return a == b


def flatten(d, parent_key='', sep='.', include_dict=True):
    """
    Flatten nested dictionary.
    Used by get_types. Do not use on its own. Values in lists are treated specially.

    :param parent_key: used for recursion. Leave blank
    :param sep: field seperator

    Examples
    --------
    >>> flatten({'a':{'b':1, 'c':[{'ca':{'cb':54}}]}, 'd':5})
    {'a': <class 'dict'>, 'a.b': 1, 'a.c': [{'ca': {'cb': 54}}], 'd': 5}

    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.append((new_key, dict))
            items.extend(flatten(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            items.append((new_key, list))
            items.extend(flatten(v[0], new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def is_non_str_iter(x):
    """
    returns if input is iterable but not a string. For example: list, tuple, set
    """
    return isinstance(x, collections.Iterable) and not isinstance(x, str)


def get_types(d):
    """
    Represent dict as dict of types

    In lists, check to make sure all values in list are of the same type
    In a list of dicts, makes sure all values for each key in the list of dictionaries are of the same type,
    and generates the aggregate of the list of dicts as a dict

    Return as flattened dict

    :param d:
    :return:

    Examples
    --------
    >>> get_types({'a': 1, 'b': 'hello', 'c': None, 'd': {'da': 1, 'db': ['1','2','3'], 'dc': {'dca': 4}}, 'e': [1,2,3],
    ...            'f': [{'fa': 1, 'fb': '2'}, {'fa': 11, 'fb': '22'}]})
    {'a': <class 'int'>,
     'b': <class 'str'>,
     'c': <class 'float'>,
     'd': <class 'dict'>,
     'd.da': <class 'int'>,
     'd.db': typing.List<~T>[str],
     'd.dc': <class 'dict'>,
     'd.dc.dca': <class 'int'>,
     'e': typing.List<~T>[int],
     'f': <class 'dict'>,
     'f.fa': <class 'int'>,
     'f.fb': <class 'str'>}


    """
    d_type = dict()
    for k, v in d.items():
        if isinstance(v, collections.MutableMapping):  # dict
            d_type[k] = get_types(v)
        elif is_non_str_iter(v):  # list, set, tuple
            if len(v) == 0:
                d_type[k] = List
            else:
                iterable_types = set(type(x) for x in v)
                assert len(iterable_types) == 1, "multiple types found in {}. Key: {}".format(v, k)
                if isinstance(next(iter(v)), collections.MutableMapping):
                    d_type[k] = [merge_type_dict([get_types(item) for item in v])]
                else:
                    iterable_type = list(iterable_types)[0]
                    d_type[k] = List[iterable_type]
        elif isinstance(v, type(None)):
            # special case: None is treated as a float
            d_type[k] = float
        else:  # str, int, float, etc
            d_type[k] = type(v)
    return flatten(d_type)


def compare_types(dlist):
    global_d = dict()
    for d in dlist:
        d = get_types(d)
        for k, v in d.items():
            if k in global_d:
                if (hasattr(v, "__args__") and v.__args__ is not None) or not hasattr(v, "__args__"):
                    # hack for empty lists with type None
                    assert v == global_d[k], "inconsistent types {} and {} in {}".format(v, global_d[k], k)
            else:
                if hasattr(v, "__args__"):
                    # hack for empty lists with type None
                    if v.__args__ is not None:
                        global_d[k] = v
                else:
                    global_d[k] = v
    return global_d
