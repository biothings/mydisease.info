from collections import defaultdict
from biothings.utils.dataload import dict_sweep, unlist
import pandas as pd
import json

def parse_diseaseid(did: str):
    """
    The 'DiseaseID' column sometimes starts with the identifier prefix, and sometime doesnt
    prefixes are {'MESH:','OMIM:'}
    if an ID starts with 'C' or 'D', its MESH, if its an integer: 'OMIM'
    """
    if did.startswith("OMIM:") or did.startswith("MESH:"):
        return did.split(":", 1)[0] + ":" + did.split(":", 1)[1]
    if did.startswith('C') or did.startswith('D'):
        return 'MESH:' + did
    if did.isdigit():
        return "OMIM:" + did
    raise ValueError(did)

def process_go(file_path_go, go_category):
    # read in the data frame
    df_disease_go = pd.read_csv(file_path_go, sep=',', comment='#', compression='gzip', names=['DiseaseName', 'DiseaseID', 'go_name', 'go_id', 'inference_gene_quantity', 'inference_gene_symbol'])
    # add new column called source
    df_disease_go['source'] = 'CTD'
    # rename the disease ID, add prefix to it
    df_disease_go['DiseaseID'] = df_disease_go['DiseaseID'].map(parse_diseaseid)
    field_split = df_disease_go['inference_gene_symbol'].dropna().astype(str).str.split("|")
    # change list of 1 into string
    for i, _item in enumerate(field_split):
        if len(_item) == 1:
            field_split[i] = _item[0]
    df_disease_go['inference_gene_symbol'][field_split.index] = field_split
    d = []
    for did, subdf in df_disease_go.groupby('DiseaseID'):
        records = subdf.to_dict(orient='records')
        go_related = [{k: v for k, v in record.items() if k not in {'DiseaseName', 'DiseaseID'}} for record in records]
        drecord = {'_id': did, 'go': {go_category: go_related}}
        d.append(drecord)
    return {x['_id']: x['go'] for x in d}

