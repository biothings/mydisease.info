import gzip
import json
import os
import subprocess
from collections import defaultdict

import pandas as pd
from mydisease import DATA_DIR
from mydisease.dataload.ctdbase.download_raw_data import relationships
import logging
logger = logging.getLogger(__name__)

pd.set_option('display.width', 1000)


def preprocess_genes(file_path):
    """
    read in csv line by line and output as a semicolon separated file without quotes, taking only the first 4 columns
    can't do this using unix tools because of the quoted fields

    :param file_path:
    :return:
    """
    logger.debug("preprocessing genes file")
    f = gzip.open(file_path, 'rt', encoding='utf-8')
    out_file = os.path.join(os.path.dirname(file_path), "CTD_genes_diseases.csv.temp")
    logger.debug("writing: {}".format(out_file))
    with open(out_file, 'w') as f_out:
        for df in pd.read_csv(f, delimiter=",", comment="#", header=None, chunksize=100000, low_memory=False):
            df4 = df[[0, 1, 2, 3]]
            f_out.write(df4.to_csv(path=None, sep=";", header=False, index=False))

    out_file2 = os.path.join(os.path.dirname(file_path), "CTD_genes_diseases_processed.csv")
    logger.debug("writing: {}".format(out_file2))
    with open(out_file2, 'w') as f_out2:
        subprocess.Popen(["uniq", out_file], stdout=f_out2)

    logger.debug("done preprocessing genes file")
    return out_file2


def parse_genes(file_path):
    df = pd.read_csv(file_path, delimiter=";", names=['GeneSymbol', 'GeneID', 'DiseaseName', 'DiseaseID'])
    return df


def parse_diseaseid(did: str):
    """ The 'DiseaseID' column sometimes starts with the identifier prefix, and sometime doesnt
    prefixes are {'MESH:','OMIM:'}
    if an ID starts with 'C' or 'D', its MESH, if its an integer: 'OMIM'
    """
    if did.startswith("OMIM:") or did.startswith("MESH:"):
        return did
    if did.startswith('C') or did.startswith('D'):
        return 'MESH:' + did
    if did.isdigit():
        return "OMIM:" + did
    print("warning: " + did)
    return did


def parse_file(file_path):
    """
    Return a dataframe from raw data
    :param f:
    :return:
    """
    f = gzip.open(os.path.join(DATA_DIR, file_path), 'rt', encoding='utf-8')
    line = next(f)
    while not line.startswith("# Fields:"):
        line = next(f)

    fields = next(f)[1:].strip().split(",")

    df = pd.read_csv(f, delimiter=",", comment="#")
    df.columns = fields

    df['DiseaseID'] = df['DiseaseID'].map(parse_diseaseid)

    return df


keep_fields = {'GO_BP': 'GOID',
               'GO_CC': 'GOID',
               'GO_MF': 'GOID',
               'pathways': 'PathwayID',
               'chemicals': 'ChemicalID',
               'genes': 'GeneID'}


def parse(use_temp=False):
    """
    Main function to parse everything
    :return:

    """
    d = defaultdict(dict)
    for relationship, file_path in relationships.items():
        print(relationship)
        if relationship == "genes":
            # parse this file separately
            if use_temp:
                file_path = os.path.join(DATA_DIR, "CTD_genes_diseases_processed.csv")
            else:
                file_path = preprocess_genes(os.path.join(DATA_DIR, file_path))
            df = parse_genes(file_path)
        else:
            df = parse_file(file_path)
        print(df.shape)
        for diseaseID, subdf in df.groupby("DiseaseID"):
            d[diseaseID][relationship] = list(set(list(subdf[keep_fields[relationship]].astype(str))))

    d = dict(d)
    with open("ctdbase.json", 'w') as f:
        json.dump(d, f, indent=2)

if __name__ == "__main__":
    parse(use_temp=False)