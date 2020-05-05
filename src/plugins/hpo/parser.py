from collections import defaultdict
from biothings.utils.dataload import dict_sweep, unlist
import pandas as pd
import json
import os


# Build a dictionary to map from UMLS identifier to MONDO ID
def construct_orphanet_omim_to_mondo_library(file_path_mondo):
    umls_2_mondo = defaultdict(list)
    with open(file_path_mondo) as f:
        data = json.loads(f.read())
        mondo_docs = data['graphs'][0]['nodes']
        for record in mondo_docs:
            if 'id' in record and record['id'].startswith('http://purl.obolibrary.org/obo/MONDO_'):
                if 'meta' in record and 'xrefs' in record['meta']:
                    for _xref in record['meta']['xrefs']:
                        prefix = _xref['val'].split(':')[0]
                        if prefix.lower() == 'orphanet' or prefix.lower() == 'omim':
                            mondo_id = 'MONDO:' + record['id'].split('_')[-1]
                            umls_2_mondo[_xref['val'].upper()].append(mondo_id)
    return umls_2_mondo


def process_disease2hp(file_path_disease_hpo):
    df_disease_hpo = pd.read_csv(file_path_disease_hpo, sep="\t", skiprows=4)
    df_disease_hpo = df_disease_hpo.rename(index=str, columns={"DiseaseName": "disease_name", "DatabaseID": "disease_id"})
    # df_disease_hpo['disease_id'].replace('ORPHA', 'ORPHANET',inplace=True)
    # df_disease_hpo['disease_id'] = df_disease_hpo.apply(lambda row: row["#DB"] + ":" + str(row["DB_Object_ID"]), axis=1)
    df_disease_hpo = df_disease_hpo.where((pd.notnull(df_disease_hpo)), None)
    d = []
    for did, subdf in df_disease_hpo.groupby('disease_id'):
        did = did.replace('ORPHA', 'ORPHANET')
        records = subdf.to_dict(orient='records')
        pathway_related = []
        for record in records:
            record_dict = {}
            for k, v in record.items():
                # name the field based on pathway database
                if k == 'sex':
                    record_dict[k.lower()] = v.lower()
                elif k not in {'Date_Created', 'DB_Object_ID', 'DB_Reference', 'disease_id', 'disease_name'}:
                    record_dict[k.lower()] = v
            pathway_related.append(record_dict)
        drecord = {'_id': did, 'hpo': pathway_related, 'disease_name': records[0]['disease_name']}
        d.append(drecord)
    return {x['_id']: [x['hpo'], x['disease_name']] for x in d}


# def calculate_mondo_mismatch():
#     d_hpo = process_disease2hp(file_path_disease_hpo)
#     orphanet_omim_2_mondo = construct_orphanet_omim_to_mondo_library(file_path_mondo)
#     matched = []
#     mismatched = []
#     for disease_id in d_hpo.keys():
#         if disease_id in orphanet_omim_2_mondo:
#             matched.append(disease_id)
#         else:
#             mismatched.append(disease_id)
#     return {'matched': matched, 'mismatch': mismatched}

def load_data(data_folder):
    file_path_disease_hpo = os.path.join(data_folder, 'phenotype.hpoa')
    file_path_mondo = os.path.join(data_folder, 'mondo.json')
    d_hpo = process_disease2hp(file_path_disease_hpo)
    orphanet_omim_2_mondo = construct_orphanet_omim_to_mondo_library(file_path_mondo)
    for disease_id in d_hpo.keys():
    #for disease_id in set(list(d_go_bp.keys()) + list(d_go_mf.keys()) + list(d_go_cc.keys()) + list(d_pathway.keys())):
        if disease_id in orphanet_omim_2_mondo:
            mondo_id = orphanet_omim_2_mondo[disease_id]
            for _mondo in mondo_id:
                if disease_id.startswith('OMIM'):
                    _doc = {'_id': _mondo,
                            'hpo': {
                                'disease_name': d_hpo.get(disease_id, {})[1],
                                'omim': disease_id.split(':')[1],
                                'phenotype_related_to_disease': d_hpo.get(disease_id, {})[0]
                                }
                           }
                elif disease_id.startswith('ORPHANET'):
                    _doc = {'_id': _mondo,
                            'hpo': {
                                'disease_name': d_hpo.get(disease_id, {})[1],
                                'orphanet': disease_id.split(':')[1],
                                'phenotype_related_to_disease': d_hpo.get(disease_id, {})[0]
                                }
                           }
                else:
                    print(disease_id)
                _doc = (dict_sweep(unlist(_doc), [None]))
                yield _doc

        else:
            if disease_id.startswith('OMIM'):
                _doc = {'_id': disease_id,
                        'hpo': {
                            'disease_name': d_hpo.get(disease_id, {})[1],
                            'omim': disease_id.split(':')[1],
                            'phenotype_related_to_disease': d_hpo.get(disease_id, {})[0]
                            }
                        }
            elif disease_id.startswith('ORPHANET'):
                _doc = {'_id': disease_id,
                        'hpo': {
                            'disease_name': d_hpo.get(disease_id, {})[1],
                            'orphanet': disease_id.split(':')[1],
                            'phenotype_related_to_disease': d_hpo.get(disease_id, {})[0]
                            }
                        }
            else:
                _doc = {'_id': disease_id,
                        'hpo': {
                            'disease_name': d_hpo.get(disease_id, {})[1],
                            'decipher': disease_id.split(':')[1],
                            'phenotype_related_to_disease': d_hpo.get(disease_id, {})[0]
                            }
                        }
            _doc = (dict_sweep(unlist(_doc), [None]))
            yield _doc