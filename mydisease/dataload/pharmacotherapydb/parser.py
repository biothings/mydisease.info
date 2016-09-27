from pymongo import MongoClient
from . import file_path, __METADATA__

import pandas as pd

field = __METADATA__['field']

def _parse():
    df = pd.read_csv(file_path, header=0, sep='\t')
    d = []
    for diseaseID, subdf in df.groupby("doid_id"):
        del subdf['doid_id']
        del subdf['disease']
        sub = subdf.to_dict(orient="records")
        d.append({'_id': diseaseID.lower(), 'indications': sub})
    return d


def parse(mongo_collection=None, drop=True):
    if mongo_collection:
        db = mongo_collection
    else:
        client = MongoClient()
        db = client.mydisease[field]
    if drop:
        db.drop()
    d = _parse()
    db.insert_many(d)

