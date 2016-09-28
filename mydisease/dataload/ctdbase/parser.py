import gzip
import os

import pandas as pd
from mydisease import DATA_DIR
from pymongo import MongoClient
from tqdm import tqdm

from . import relationships

columns_rename = {'GOID': 'go',
                  'InferenceGeneSymbols': 'inference_gene_symbols',
                  'PathwayID': 'pathway',
                  'CasRN': 'casrn',
                  'ChemicalID': 'chemical',
                  'DirectEvidence': 'direct_evidence',
                  'InferenceGeneSymbol': 'inference_gene_symbol',
                  'InferenceScore': 'inference_score',
                  'OmimIDs': 'omim',
                  'GeneID': 'gene',
                  'InferenceChemicalName': 'inference_chemical_name',
                  'PubMedIDs': 'pubmed'}


def parse_diseaseid(did: str):
    """
    The 'DiseaseID' column sometimes starts with the identifier prefix, and sometime doesnt
    prefixes are {'MESH:','OMIM:'}
    if an ID starts with 'C' or 'D', its MESH, if its an integer: 'OMIM'
    """
    if did.startswith("OMIM:") or did.startswith("MESH:"):
        return did.split(":", 1)[0].lower() + ":" + did.split(":", 1)[1]
    if did.startswith('C') or did.startswith('D'):
        return 'mesh:' + did
    if did.isdigit():
        return "omim:" + did
    raise ValueError(did)


def parse_csv_to_df(f):
    line = next(f)
    while not line.startswith("# Fields:"):
        line = next(f)
    # parse the column headers from the comments
    fields = next(f)[1:].strip().split(",")
    df = pd.read_csv(f, delimiter=",", comment="#")
    df.columns = fields

    # split pipe-delimited fields
    fields_split = {'DirectEvidence', 'OmimIDs', 'PubMedIDs', 'InferenceGeneSymbols'} & set(fields)
    for field in fields_split:
        # don't split NaN
        field_split = df[field].dropna().astype(str).str.split("|")
        df[field][field_split.index] = field_split

    df['DiseaseID'] = df['DiseaseID'].map(parse_diseaseid)
    return df


def get_columns_to_keep(relationship: str):
    if relationship in {'GO_BP', 'GO_CC', 'GO_MF'}:
        columns_keep = ['GOID', 'InferenceGeneSymbols']
    elif relationship == "pathways":
        columns_keep = ['PathwayID', 'InferenceGeneSymbol']
    elif relationship == "chemicals":
        columns_keep = ['CasRN', 'ChemicalID', 'DirectEvidence', 'InferenceGeneSymbol', 'InferenceScore', 'OmimIDs',
                        'PubMedIDs']
    elif relationship == "genes":
        columns_keep = ['GeneID', 'DirectEvidence', 'InferenceScore', 'InferenceChemicalName', 'OmimIDs', 'PubMedIDs']
    return columns_keep


def parse_df(db, df, relationship: str):
    """
    df is parsed and added to mongodb (db)
    """
    columns_keep = get_columns_to_keep(relationship)
    total = len(set(df.DiseaseID))
    for diseaseID, subdf in tqdm(df.groupby("DiseaseID"), total=total):
        sub = subdf[columns_keep].rename(columns=columns_rename).to_dict(orient="records")
        sub = [{k: v for k, v in s.items() if v == v} for s in sub]  # get rid of nulls
        db.update_one({'_id': diseaseID}, {'$set': {relationship.lower(): sub}}, upsert=True)


def process_genes(db, f):
    """
    # for the genes file, which is enormous, we need to do something different
    # basically same as others, but in chunks
    d is modified in place!!
    
    note: this will fail
    WriteError: Resulting document after update is larger than 16777216

    """
    raise NotImplementedError()
    chunksize = 100000
    names = ['GeneSymbol', 'GeneID', 'DiseaseName', 'DiseaseID', 'DirectEvidence',
             'InferenceChemicalName', 'InferenceScore', 'OmimIDs', 'PubMedIDs']
    for df in tqdm(pd.read_csv(f, delimiter=",", comment="#", header=None, chunksize=chunksize,
                               low_memory=False, names=names), total=49867785 / chunksize):
        fields_split = ['DirectEvidence', 'OmimIDs', 'PubMedIDs']
        for field in fields_split:
            field_split = df[field].dropna().astype(str).str.split("|")
            df[field][field_split.index] = field_split
        columns_keep = get_columns_to_keep('genes')
        df['DiseaseID'] = df['DiseaseID'].map(parse_diseaseid)
        for diseaseID, subdf in df.groupby("DiseaseID"):
            sub = subdf[columns_keep].to_dict(orient="records")
            # get rid of nulls
            sub = [{k: v for k, v in s.items() if v == v} for s in sub]
            db.update_one({'_id': diseaseID}, {'$push': {relationship: {'$each': sub}}}, upsert=True)


def parse(mongo_collection=None, drop=True):
    if mongo_collection:
        db = mongo_collection
    else:
        client = MongoClient()
        db = client.mydisease.ctdbase
    if drop:
        db.drop()
    for relationship, file_path in relationships.items():
        print(relationship)
        with gzip.open(os.path.join(DATA_DIR, file_path), 'rt', encoding='utf-8') as f:
            if relationship == "genes":
                # process_genes(db, f)
                print("skipping genes")
                pass
            else:
                df = parse_csv_to_df(f)
                parse_df(db, df, relationship)
