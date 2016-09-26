import gzip
import json
import os
from collections import defaultdict

import pandas as pd

from mydisease import DATA_DIR
from mydisease.dataload.ctdbase.download_raw_data import relationships

pd.set_option('display.width', 1000)


def parse_file(f):
    line = next(f)
    while not line.startswith("# Fields:"):
        line = next(f)

    fields = next(f)[1:].strip().split(",")

    df = pd.read_csv(f, delimiter=",", comment="#")
    df.columns = fields

    # split pipe-delimited fields
    fields_split = set(['DirectEvidence', 'OmimIDs', 'PubMedIDs', 'InferenceGeneSymbols']) & set(fields)
    for field in fields_split:
        df[field] = df[field].astype(str).str.split("|")

    return df


d = defaultdict(dict)
columns_remove = ['DiseaseName', 'DiseaseID']
for relationship, file_path in relationships.items():
    print(relationship)
    f = gzip.open(os.path.join(DATA_DIR, file_path), 'rt', encoding='utf-8')
    df = parse_file(f)

    columns_keep = df.columns[df.columns.isin(set(df.columns) - set(columns_remove))]
    for diseaseID, subdf in df.groupby("DiseaseID"):
        sub = subdf[columns_keep].to_dict(orient="records")
        d[diseaseID][relationship] = sub

d = dict(d)
with open("out.json", 'w') as f:
    json.dump(d, f, indent=2)
