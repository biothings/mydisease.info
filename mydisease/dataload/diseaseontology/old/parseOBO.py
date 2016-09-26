import re
from itertools import chain

import networkx
import requests
from mydisease.utils import read_obo
from networkx.readwrite import json_graph
import json


def graph_to_d(graph):
    """

    :param graph: A networkx graph made from reading ontology
    :type graph: networkx.classes.multidigraph.MultiDiGraph
    :return:
    """
    node_link_data = json_graph.node_link_data(graph)
    nodes = node_link_data['nodes']

    idx_id = {idx: node['id'] for idx,node in enumerate(nodes)}
    for link in node_link_data['links']:
        # store the edges (links) within the graph
        key = link['key']
        source = link['source']
        target = link['target']

        if key not in nodes[source]:
            nodes[source][key] = set()
        nodes[source][key].add(idx_id[target])

    d = {node['id']: node for node in nodes}

    return d


def parse_synonym(line: str):
    # line = "synonym: \"The other white meat\" EXACT MARKETING_SLOGAN [MEAT:00324, BACONBASE:03021]"
    return line[line.index("\"")+1:line.rindex("\"")] if line.count("\"") == 2 else line


def parse_def(line: str):
    # line = "\"A description.\" [url:http\://www.ncbi.goc/123, url:http\://www.ncbi.nlm.nih.gov/pubmed/15318016]"
    definition = line[line.index("\"")+1:line.rindex("\"")] if line.count("\"") == 2 else line
    if line.endswith("]") and line.count("["):
        left_bracket = [m.start() for m in re.finditer('\[', line)]
        right_bracket = [m.start() for m in re.finditer('\]', line)]
        endliststr = line[left_bracket[-1]+1:right_bracket[-1]-1]
        endlist = [x.strip() for x in endliststr.split(", ")]
        return definition, endlist
    else:
        return definition, None


url = "http://purl.obolibrary.org/obo/doid.obo"
r = requests.get(url)
graph = read_obo(r.text.splitlines())
d = graph_to_d(graph)


# graph.node['DOID:2377']
# graph.edges('DOID:2377', keys=True)
# d['DOID:2377']

for value in d.values():
    if 'synonym' in value:
        value['synonym'] = list(map(parse_synonym, value['synonym']))
    if 'def' in value:
        value['def'],ref = parse_def(value['def'])
        if ref:
            value['def_ref'] = ref


def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

with open("DO_obo.json", 'w') as f:
    json.dump(d, f, indent=2, default=set_default)