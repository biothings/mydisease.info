import os, pandas, csv, re
import numpy as np
from biothings.utils.dataload import dict_convert, dict_sweep
from biothings import config
logging = config.logger

import networkx
import obonet as obonet
import json
import requests


def load_annotations(data_folder):
    """Load annotations function

    Use obonet and networkx packages to transform .obo data file into
    dictionaries, where id_ is based off of DOID, but changed to MONDO
    if available on MyDisease.info 

    Addtionally, use xref key style seen on MyDisease.info (if availble)
    """
    url = os.path.join(data_folder,"doid.obo")
    graph = obonet.read_obo(url)
    all_doids = list(graph.nodes())
    doid_mondo_dict = create_doid_mondo_dict(all_doids)
    for id_, data in graph.nodes(data=True):
        disease_ontology = {
            "doid": id_,
            "name": data["name"],
            "def": data["def"] if "def" in data else "",
            "synonyms": get_synonyms(data),
            "xrefs": get_xrefs(data),
            "children": [[i][0][0] for i in list(graph.in_edges(id_, keys=True))],
            "descendants": list(networkx.ancestors(graph, id_)),
            "parents": [[i][0][1] for i in list(graph.out_edges(id_, keys=True))],   
            "ancestors": list(networkx.descendants(graph, id_))
        }
        xrefs = {}
        current_dict = {
            "_id": doid_mondo_dict[id_] if id_ in doid_mondo_dict else id_,
            "disease_ontology": disease_ontology,
        }
        yield(current_dict)


# dictionary where keys are xref keys in Disease Ontology and values are xref
# keys from MyDisease.info  
MONdO_XREF_DICT = {
        "UMLS_CUI": 'umls_cui',
        "ICD10CM": 'icd10',
        "MESH": 'mesh',
        "OMIM": 'omim',
        "GARD": 'gard',
        "NCI": 'ncit',
        "ORDO": 'ordo',
        "ICDO": 'icdo',
        "MEDDRA": 'meddra',
        "KEGG": 'kegg',
        "ICD9CM": 'icd9',
        "GArD": 'gard',
        "EFO": 'efo',
        "DERMO": 'dermo',
}

def create_doid_mondo_dict(all_doids):
    """Create DOID:MONDO dictionary

    Query MyDisease.info to see if MONDO id exists for each DOID given. If so,
    save in dicitonary such that each key = DOID and value = MONDO
    """
    doid_mondo_dict = {}
    start = 0;
    interval = 900
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    while(start < len(all_doids)):
        q = ','.join(all_doids[start:start+interval])
        params = 'q='+ q + "&scopes=mondo.xrefs.doid"
        res = requests.post('http://mydisease.info/v1/query', data=params, headers=headers)
        response_json = json.loads(res.text)
        for i in range(0,len(response_json)):
            if "_id" in response_json[i]:
                doid_mondo_dict[response_json[i]["query"]] = response_json[i]["_id"]
        start = start + interval
    return doid_mondo_dict

def get_synonyms(data):
    """Format synonyms as dicionary

    exact and related synonyms are the keys, and their values are in lists
    """
    if 'synonym' in data:
        syn_dict = {}
        exact = []
        related = []
        for syn in data['synonym']:
            if 'EXACT' in syn: 
                match = re.findall(r'\"(.+?)\"', syn)
                exact = exact + match
            elif 'RELATED' in syn: 
                match = re.findall(r'\"(.+?)\"', syn)
                related = related + match
        synonyms = {}
        if len(exact) > 0:
            synonyms["exact"] = exact
        if len(related) > 0:
            synonyms["related"] = related
        return synonyms
    else:
        return {}

def get_xrefs(data):
    """Format xrefs

    Return xrefs in dictionary, where keys match MyDisease.info xref keys when
    available. If not available, convert xref key to lowercase. Additionally, 
    if more than 1 value for specific xref, transform to list, otherwise each
    value kept as string.  
    """
    xrefs = {}
    if 'xref' in data:
        for xref in data['xref']:
            xref = xref.split(":")
            if xref[0] in MONdO_XREF_DICT:
                xref[0] = MONdO_XREF_DICT[xref[0]]
            else: 
                xref[0] = xref[0].lower()
            if xref[0] in xrefs:
                xrefs[xref[0]] = [xrefs[xref[0]]] if isinstance(xrefs[xref[0]], str) else xrefs[xref[0]]
                xrefs[xref[0]].append(xref[1])
            else:
                xrefs[xref[0]] = xref[1]
        return xrefs
    else:
        return xrefs