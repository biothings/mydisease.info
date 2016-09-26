import re
from itertools import chain
from typing import List

import networkx
from mydisease.utils import read_obo
from mydisease.utils.common import list2dict
from networkx.readwrite import json_graph
from pymongo import MongoClient

from . import file_path


def graph_to_d(graph):
    """
    :param graph: A networkx graph made from reading ontology
    :type graph: networkx.classes.multidigraph.MultiDiGraph
    :return:
    """
    node_link_data = json_graph.node_link_data(graph)
    nodes = node_link_data['nodes']

    idx_id = {idx: node['id'] for idx, node in enumerate(nodes)}
    for link in node_link_data['links']:
        # store the edges (links) within the graph
        key = link['key']
        source = link['source']
        target = link['target']

        if key not in nodes[source]:
            nodes[source][key] = set()
        nodes[source][key].add(idx_id[target])

    # for mongo insertion
    for node in nodes:
        node['_id'] = node['id'].lower()
        if "alt_id" in node:
            node['alt_id'] = [x.lower() for x in node['alt_id']]
        if "is_a" in node:
            node['is_a'] = [x.lower() for x in node['is_a']]
        if "property_value" in node:
            del node['property_value']
        del node['id']
        for k, v in node.items():
            if isinstance(v, set):
                node[k] = list(v)
    d = {node['_id']: node for node in nodes}

    return d


def parse_synonym(line: str):
    # line = "synonym: \"The other white meat\" EXACT MARKETING_SLOGAN [MEAT:00324, BACONBASE:03021]"
    return line[line.index("\"") + 1:line.rindex("\"")] if line.count("\"") == 2 else line


def parse_def(line: str):
    """
    Parse definition field.
    Returns a tuple(definition, list of crosslink urls)
    
    >>> parse_def("\"A description.\" [url:http://www.ncbi.goc/123, url:http://www.ncbi.nlm.nih.gov/pubmed/15318016]")
    ('A description.', ['url:http\\://www.ncbi.goc/123', 'url:http\\://www.ncbi.nlm.nih.gov/pubmed/1531801'])
    
    """
    definition = line[line.index("\"") + 1:line.rindex("\"")] if line.count("\"") == 2 else line
    if line.endswith("]") and line.count("["):
        left_bracket = [m.start() for m in re.finditer('\[', line)]
        right_bracket = [m.start() for m in re.finditer('\]', line)]
        endliststr = line[left_bracket[-1] + 1:right_bracket[-1]]
        endlist = [x.strip().replace("\\\\", "").replace("\\", "") for x in endliststr.split(", ")]
        return definition, endlist
    else:
        return definition, None


def parse_xref(xrefs: List[str]):
    """
    Parse xref field. Input is list of strings (xref IDs)
    Normalizes prefix strings (MSH -> MESH, ORDO -> Orphanet) and converts prefix to lowercase
    Returns dict[ID prefix: list of IDs without prefix]
    
    >>> parse_xref(['MSH:D006954',  'SNOMEDCT_US_2016_03_01:190781009',  'SNOMEDCT_US_2016_03_01:34349009',  'UMLS_CUI:C0020481'])
    {'MESH': ['D006954'],
     'SNOMEDCT_US_2016_03_01': ['190781009', '34349009'],
     'UMLS_CUI': ['C0020481']}
    
    """

    xrefs = [x for x in xrefs if ":" in x]
    xrefs = [x.split(":", 1)[0].lower() + ":" + x.split(":", 1)[1] for x in xrefs]
    for n, xref in enumerate(xrefs):
        if xref.startswith("msh:"):
            xrefs[n] = "mesh:" + xref.split(":", 1)[1]
        if xref.startswith("ordo:"):
            xrefs[n] = "orphanet:" + xref.split(":", 1)[1]
    return list2dict(xrefs)


def parse(mongo_collection=None, drop=True):
    if mongo_collection:
        db = mongo_collection
    else:
        client = MongoClient()
        db = client.mydisease.disease_ontoloy
    if drop:
        db.drop()
    graph = read_obo(open(file_path).readlines())
    d = graph_to_d(graph)

    for value in d.values():
        if 'xref' in value:
            value['xref'] = parse_xref(value['xref'])
        if 'synonym' in value:
            value['synonym'] = list(map(parse_synonym, value['synonym']))
        if 'def' in value:
            value['def'], ref = parse_def(value['def'])
            if ref:
                if 'xref' in value:
                    value['xref'].update(parse_xref(ref))
                else:
                    value['xref'] = parse_xref(ref)

    db.insert_many(d.values())

