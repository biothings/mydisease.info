from collections import defaultdict
from biothings.utils.dataload import dict_sweep, unlist
import pandas as pd
import json
import os


##############################################################################################
#The source data contains two files:
# File 1: http://www.disgenet.org/ds/DisGeNET/results/all_gene_disease_associations.tsv.gz
#         This file contain all gene disease association in DisGeNET
#         Including data from both curated sources (e.g. UNIPROT, CTD) as well as auto extracted
#         ones, e.g. BeFree
# File 2: http://www.disgenet.org/ds/DisGeNET/results/all_variant_disease_pmid_associations.tsv.gz
#         This file contains all gene variant associations in DisGeNET
# Two files will be merged based on the disease ID
# The primary disease ID used in DisGeNet is UMLS concept unique identifier
# The structure of the output JSON doc will be as followed:
# {
#   "_id": "MONDO:####",
#   "disgenet": {
#        "disease":{
#             "umls": "D####",
#             "disease_name": "### ###",
#             "disease_type": "###"
#        },
#        "genes_related_to_disease": {
#             "gene_id": "###",
#             "gene_name": "####",
#             "n_pmids": ###,
#             "n_snps": ###,
#             "source": ["###"],
#             "score": ####
#        },
#        "variants_related_to_disease": {
#             "rsid": "###",
#             "chromosome": "####",
#             "position": "####",
#             "pmid": "###",
#             "score": "###",
#             "source": "###"
#        }
#    }
#}
##############################################################################################

def process_gene(file_path_gene_disease):
    df_gene_disease = pd.read_csv(file_path_gene_disease, encoding="ISO-8859-1", sep="\t", comment="#", compression="gzip")
    rename_gene = {'diseaseId': 'umls',
                   'geneId': 'gene_id',
                   'geneSymbol': 'gene_name',
                   'diseaseName': 'disease_name',
                   'NofPmids': 'n_pmids',
                   'NofSnps': 'n_snps'}
    # source field could be multiple data sources concatenated by ";", break them into a list
    df_gene_disease = df_gene_disease.where((pd.notnull(df_gene_disease)), None)
    source_col = df_gene_disease.source
    new_source_col = []
    for _row in source_col:
        if _row and len(_row) == 1:
            new_source_col.append(_row[0])
        else:
            new_source_col.append(_row)
    df_gene_disease.source = new_source_col
    d = []
    # rename pandas columns
    df_gene_disease = df_gene_disease.rename(columns=rename_gene)
    for did, subdf in df_gene_disease.groupby("umls"):
        records = subdf.to_dict(orient='records')
        gene_related = [{k: v for k, v in record.items() if k not in {'umls', 'disease_name'}} for record in records]
        drecord = {'_id': did.replace("umls", "umls_cui"), 'genes_related_to_disease': gene_related}
        d.append(drecord)
    return {x['_id']: x['genes_related_to_disease'] for x in d}


def process_snp(file_path_snp_disease):
    df_snp = pd.read_csv(file_path_snp_disease, sep='\t', comment='#', compression='gzip')
    rename_variant = {'diseaseId': 'umls',
                      'diseaseName': 'disease_name',
                      'originalSource': 'source',
                      'pmid': 'pubmed',
                      'snpId': 'rsid',
                      'chromosome': "chrom",
                      'position': 'pos',
                      'diseaseType': 'disease_type',
                      'originalSource': 'source',
                      'sentence': 'description'}
    # rename columns
    df_snp = df_snp.rename(columns=rename_variant)
    # change nan values to none
    df_snp = df_snp.where((pd.notnull(df_snp)), None)
    # source field could be multiple data sources concatenated by ";", break them into a list
    source_col = df_snp.source
    new_source_col = []
    for _row in source_col:
        if _row and len(_row) == 1:
            new_source_col.append(_row[0])
        else:
            new_source_col.append(_row)
    df_snp.source = new_source_col
    d = []
    for did, subdf in df_snp.groupby("umls"):
        records = subdf.to_dict(orient='records')
        # change string value to integers
        for record in records:
            if 'pubmed' in record and record['pubmed']:
                record['pubmed'] = int(record['pubmed'])
            if 'pos' in record and record['pos']:
                record['pos'] = int(record['pos'])
        variant_related = [{k: v for k, v in record.items() if k not in {'umls', 'disease_name', 'disease_type'}} for record in records]
        #records = [{k: v for k, v in record.items() if k not in {'_id', 'label'}} for record in records]
        drecord = {'_id': did.replace("umls", "umls_cui"), 'variants_related_to_disease': variant_related}
        d.append(drecord)
    return {x['_id']: x['variants_related_to_disease'] for x in d}

def process_xrefs(file_path_disease_mapping):
    df_disease_mapping = pd.read_csv(file_path_disease_mapping, sep="\t", comment="#", compression="gzip")
    d = []
    for did, subdf in df_disease_mapping.groupby("diseaseId"):
        records = subdf.to_dict(orient='records')
        drecord = {'_id': did.replace("umls", "umls_cui"), 'xrefs': {'umls': did.replace("umls", "umls_cui"), 'disease_name': records[0]['name']}}
        for _record in records:
            drecord['xrefs'][_record['vocabulary'].lower().replace('msh', 'mesh').replace('do', 'doid')
                                                  .replace('ordoid', 'ordo').replace('hpo', 'hp').replace('icd9cm', 'icd9')] = _record['code']
        d.append(drecord)
    return {x['_id']: x['xrefs'] for x in d}

# Build a dictionary to map from UMLS identifier to MONDO ID
def construct_umls_to_mondo_library(file_path_mondo):
    umls_2_mondo = defaultdict(list)
    with open(file_path_mondo) as f:
        data = json.loads(f.read())
        mondo_docs = data['graphs'][0]['nodes']
        for record in mondo_docs:
            if 'id' in record and record['id'].startswith('http://purl.obolibrary.org/obo/MONDO_'):
                if 'meta' in record and 'xrefs' in record['meta']:
                    for _xref in record['meta']['xrefs']:
                        prefix = _xref['val'].split(':')[0]
                        if prefix.lower() == 'umls':
                            mondo_id = 'MONDO:' + record['id'].split('_')[-1]
                            umls_2_mondo[_xref['val'][len(prefix)+1:]].append(mondo_id)
    return umls_2_mondo


def load_data(data_folder):
    file_path_mondo = os.path.join(data_folder, "mondo.json")
    file_path_gene_disease = os.path.join(data_folder, "curated_gene_disease_associations.tsv.gz")
    file_path_snp_disease = os.path.join(data_folder, "all_variant_disease_pmid_associations.tsv.gz")
    file_path_disease_mapping = os.path.join(data_folder, "disease_mappings.tsv.gz")
    d_gene = process_gene(file_path_gene_disease)
    d_snp = process_snp(file_path_snp_disease)
    d_xrefs = process_xrefs(file_path_disease_mapping)
    umls_2_mondo = construct_umls_to_mondo_library(file_path_mondo)
    for umls_id in set(list(d_gene.keys()) + list(d_snp.keys())):
        if umls_id in umls_2_mondo:
            mondo_id = umls_2_mondo[umls_id]
            for _mondo in mondo_id:
                _doc = {'_id': _mondo,
                        'disgenet': {
                            'xrefs': d_xrefs.get(umls_id, {}),
                            'genes_related_to_disease': d_gene.get(umls_id, {}),
                            'variants_related_to_disease': d_snp.get(umls_id, {})
                            }
                       }
                _doc = (dict_sweep(unlist(_doc), [None]))
                yield _doc
        else:
            _doc = {'_id': umls_id,
                    'disgenet': {
                        'xrefs': d_xrefs.get(umls_id, {}),
                        'genes_related_to_disease': d_gene.get(umls_id, {}),
                        'variants_related_to_disease': d_snp.get(umls_id, {})
                        }
                   }
            _doc = (dict_sweep(unlist(_doc), [None]))
            yield _doc