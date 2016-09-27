### Merge
import networkx as nx
from mydisease.dataload import db_names
from mydisease.utils.common import dict2list
from pymongo import MongoClient
from tqdm import tqdm


def build_id_graph():
    g = nx.Graph()
    for db_name in db_names:
        db = MongoClient().mydisease[db_name]
        for doc in db.find({'xref': {'$exists': True}}, {'xref': 1}):
            for xref in dict2list(doc['xref']):
                g.add_edge(doc['_id'], xref)
    return g


def get_equiv_doid(g, did):
    """
    For a given ID, get the DOIDs it is equivalent to within 2 hops.
    """
    if did.startswith("doid:"):
        return [did]
    if did not in g:
        return []
    equiv = list(nx.single_source_shortest_path_length(g, did, cutoff=2).keys())
    return [x for x in equiv if x.startswith("doid:")]


def parse_all():
    from mydisease.dataload.ctdbase import parser as ctdbase_parser
    from mydisease.dataload.diseaseontology import parser as diseaseontology_parser
    from mydisease.dataload.disgenet import parser as disgenet_parser
    from mydisease.dataload.hpo import parser as hpo_parser
    from mydisease.dataload.mesh import parser as mesh_parser
    # from mydisease.dataload.omim import parser as omim_parser
    from mydisease.dataload.orphanet import parser as orphanet_parser
    from mydisease.dataload.pharmacotherapydb import parser as pharmacotherapydb_parser

    ctdbase_parser.parse()
    diseaseontology_parser.parse()
    disgenet_parser.parse()
    hpo_parser.parse()
    mesh_parser.parse()
    # omim_parser.parse()
    orphanet_parser.parse()
    pharmacotherapydb_parser.parse()


def merge_one(db_name):
    mydisease = MongoClient().mydisease.mydisease
    g = build_id_graph()
    db = MongoClient().mydisease[db_name]
    if db.count() == 0:
        print("Warning: {} is empty".format(db))
    for doc in db.find():
        doids = get_equiv_doid(g, doc['_id'])
        for doid in doids:
            mydisease.update_one({'_id': doid}, {'$push': {db_name: doc}}, upsert=True)


def merge(mongo_collection=None, drop=True):
    ## merge docs
    if mongo_collection:
        mydisease = mongo_collection
    else:
        client = MongoClient()
        mydisease = client.mydisease.mydisease
    if drop:
        mydisease.drop()

    g = build_id_graph()

    # make initial primary d with all DOID docs
    db = MongoClient().mydisease.disease_ontoloy
    d = [{'_id': doc['_id'], 'disease_ontology': doc} for doc in db.find()]
    mydisease.insert_many(d)

    # fill in from other sources
    for db_name in tqdm(set(db_names) - {'disease_ontoloy'}):
        print(db_name)
        db = MongoClient().mydisease[db_name]
        if db.count() == 0:
            print("Warning: {} is empty".format(db))
        for doc in db.find():
            doids = get_equiv_doid(g, doc['_id'])
            for doid in doids:
                mydisease.update_one({'_id': doid}, {'$push': {db_name: doc}}, upsert=True)
