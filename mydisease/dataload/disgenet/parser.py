from collections import defaultdict
from itertools import chain

import pandas as pd
from pymongo import MongoClient

from . import file_path_gene_disease, file_path_snp_disease


def process_gene(file_path_gene_disease):
    df = pd.read_csv(file_path_gene_disease, sep='\t', comment='#', compression='gzip')
    rename = {'diseaseId': '_id',
              'geneId': 'gene_id',
              'geneName': 'gene_name',
              'diseaseName': 'label',
              'sourceId': 'source',
              'NofPmids': '#pmids',
              'NofSnps': '#snps'}

    df.sourceId = df.sourceId.str.split(",")
    df = df.rename(columns=rename)
    d = []
    for did, subdf in df.groupby("_id"):
        records = subdf.to_dict(orient='records')
        records = [{k: v for k, v in record.items() if k not in {'_id', 'label', 'description'}} for record in records]
        drecord = {'_id': did.replace("umls", "umls_cui"), 'genes': records}
        d.append(drecord)
    return {x['_id']: x for x in d}


def process_snp(file_path_snp_disease):
    df = pd.read_csv(file_path_snp_disease, sep='\t', comment='#', compression='gzip')
    rename = {'diseaseId': '_id',
              'geneId': 'gene_id',
              'geneSymbol': 'gene_symbol',
              'diseaseName': 'label',
              'pubmedId': 'pubmed',
              'snpId': 'rsid',
              'ALT': 'alt',
              'CHROMOSOME': "chr",
              'POS': 'pos',
              'REF': 'ref',
              'sourceId': 'source',
              'sentence': 'description'}

    df = df.rename(columns=rename)
    del df['geneSymbol_dbSNP']

    d = []
    for did, subdf in df.groupby("_id"):
        records = list(subdf.apply(lambda x: x.dropna().to_dict(), axis=1))
        for record in records:
            if 'year' in record:
                record['year'] = int(record['year'])
            if 'pubmed' in record:
                record['pubmed'] = int(record['pubmed'])
        records = [{k: v for k, v in record.items() if k not in {'_id', 'label'}} for record in records]
        drecord = {'_id': did.replace("umls", "umls_cui"), 'snps': records}
        d.append(drecord)
    return {x['_id']: x for x in d}


def parse(mongo_collection=None, drop=True):
    if mongo_collection:
        db = mongo_collection
    else:
        client = MongoClient()
        db = client.mydisease.disgenet
    if drop:
        db.drop()
    d_gene = process_gene(file_path_gene_disease)
    d_snp = process_snp(file_path_snp_disease)

    d = defaultdict(dict)
    for key in set(chain(*[list(d_gene.keys()), list(d_snp.keys())])):
        d[key] = {**d_gene.get(key, {}), **d_snp.get(key, {})}

    db.insert_many(d.values())
