from collections import defaultdict
from biothings.utils.dataload import dict_sweep, unlist
import pandas as pd
import json

from . import file_path_disease_go_bp, file_path_disease_go_cc, file_path_disease_go_mf, file_path_disease_pathway, file_path_disease_chemical, file_path_mondo


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

# Build a dictionary to map from UMLS identifier to MONDO ID
def construct_mesh_omim_to_mondo_library(file_path_mondo):
    umls_2_mondo = defaultdict(list)
    with open(file_path_mondo) as f:
        data = json.loads(f.read())
        mondo_docs = data['graphs'][0]['nodes']
        for record in mondo_docs:
            if 'id' in record and record['id'].startswith('http://purl.obolibrary.org/obo/MONDO_'):
                if 'meta' in record and 'xrefs' in record['meta']:
                    for _xref in record['meta']['xrefs']:
                        prefix = _xref['val'].split(':')[0]
                        if prefix.lower() == 'mesh' or prefix.lower() == 'omim':
                            mondo_id = 'MONDO:' + record['id'].split('_')[-1]
                            umls_2_mondo[_xref['val'].upper()].append(mondo_id)
    return umls_2_mondo

def process_go(file_path_go):
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
        go_related = [{k: v for k, v in record.items() if k not in {'DiseaseName', 'DiseaseID', 'inference_gene_quantity'}} for record in records]
        drecord = {'_id': did, 'go': go_related}
        d.append(drecord)
    return {x['_id']: x['go'] for x in d}

def process_pathway(file_path_pathway):
    # read in the data frame
    df_disease_pathway = pd.read_csv(file_path_pathway, sep=',', comment='#', compression='gzip', names=['DiseaseName', 'DiseaseID', 'pathway_name', 'pathway_id', 'inference_gene_symbol'])
    # add new column called source
    df_disease_pathway['source'] = 'CTD'
    # rename the disease ID, add prefix to it
    df_disease_pathway['DiseaseID'] = df_disease_pathway['DiseaseID'].map(parse_diseaseid)
    field_split = df_disease_pathway['inference_gene_symbol'].dropna().astype(str).str.split("|")
    # change list of 1 into string
    for i, _item in enumerate(field_split):
        if len(_item) == 1:
            field_split[i] = _item[0]
    df_disease_pathway['inference_gene_symbol'][field_split.index] = field_split
    d = []
    for did, subdf in df_disease_pathway.groupby('DiseaseID'):
        records = subdf.to_dict(orient='records')
        pathway_related = []
        for record in records:
            record_dict = {}
            for k, v in record.items():
                # name the field based on pathway database
                if k == 'pathway_id':
                    record_dict[v.split(':')[0].lower() + '_pathway_id'] = v.split(':')[1]
                elif k not in {'DiseaseName', 'DiseaseID'}:
                    record_dict[k] = v
            pathway_related.append(record_dict)
        drecord = {'_id': did, 'pathway': pathway_related}
        d.append(drecord)
    return {x['_id']: x['pathway'] for x in d}

def process_chemical(file_path_chemical):
    chunksize = 100000
    i = 0
    j = 1
    # read in the data frame
    d = []
    for df_disease_chemical in pd.read_csv(file_path_chemical, chunksize=chunksize, iterator=True, sep=',', comment='#', compression='gzip', names=['chemical_name', 'mesh_chemical_id', 'cas_registry_number', 'DiseaseName', 'DiseaseID', 'direct_evidence', 'inference_gene_symbol', 'inference_score', 'omim_id', 'pubmed']):
        df_disease_chemical.index += j
        i += 1
        # add new column called source
        df_disease_chemical['source'] = 'CTD'
        # rename the disease ID, add prefix to it
        df_disease_chemical['DiseaseID'] = df_disease_chemical['DiseaseID'].map(parse_diseaseid)
        # the record in these fields are separated by '|', need to convert them into list
        df_disease_chemical = df_disease_chemical.where((pd.notnull(df_disease_chemical)), None)
        for field_id in ['direct_evidence', 'omim_id', 'pubmed']:
            df_disease_chemical[field_id] = df_disease_chemical[field_id].apply(lambda x: x.split('|') if x and '|' in x else x)
            #df_disease_chemical[field_id] = df_disease_chemical[field_id].apply(lambda x: None if type(x) == float else x)
        for did, subdf in df_disease_chemical.groupby('DiseaseID'):
            records = subdf.to_dict(orient='records')
            chemical_related = [{k: v for k, v in record.items() if k not in {'DiseaseName', 'DiseaseID'}} for record in records]
            drecord = {'_id': did, 'chemical': chemical_related}
            d.append(drecord)
        j = df_disease_chemical.index[-1] + 1
    return {x['_id']: x['chemical'] for x in d}

def calculate_mondo_mismatch():
    d_go_bp = process_go(file_path_disease_go_bp)
    d_go_mf = process_go(file_path_disease_go_mf)
    d_go_cc = process_go(file_path_disease_go_cc)
    d_pathway = process_pathway(file_path_disease_pathway)
    mesh_omim_2_mondo = construct_mesh_omim_to_mondo_library(file_path_mondo)
    matched = []
    mismatched = []
    for disease_id in set(list(d_go_bp.keys()) + list(d_go_mf.keys()) + list(d_go_cc.keys()) + list(d_pathway.keys())):
        if disease_id in mesh_omim_2_mondo:
            matched.append(disease_id)
        else:
            mismatched.append(disease_id)
    return {'matched': matched, 'mismatch': mismatched}

def load_data():
    d_go_bp = process_go(file_path_disease_go_bp)
    d_go_mf = process_go(file_path_disease_go_mf)
    d_go_cc = process_go(file_path_disease_go_cc)
    print('loaded go data')
    d_pathway = process_pathway(file_path_disease_pathway)
    print('loaded pathway data')
    d_chemical = process_chemical(file_path_disease_chemical)
    print('loaded chemical data')
    mesh_omim_2_mondo = construct_mesh_omim_to_mondo_library(file_path_mondo)
    for disease_id in set(list(d_go_bp.keys()) + list(d_go_mf.keys()) + list(d_go_cc.keys()) + list(d_pathway.keys()) + list(d_chemical.keys())):
    #for disease_id in set(list(d_go_bp.keys()) + list(d_go_mf.keys()) + list(d_go_cc.keys()) + list(d_pathway.keys())):
        if disease_id in mesh_omim_2_mondo:
            mondo_id = mesh_omim_2_mondo[disease_id]
            for _mondo in mondo_id:
                if disease_id.startswith('MESH'):
                    _doc = {'_id': _mondo,
                            'ctd': {
                                'mesh': disease_id.split(':')[1],
                                'bp_related_to_disease': d_go_bp.get(disease_id, {}),
                                'mf_related_to_disease': d_go_mf.get(disease_id, {}),
                                'cc_related_to_disease': d_go_cc.get(disease_id, {}),
                                'pathway_related_to_disease': d_pathway.get(disease_id, {}),
                                'chemical_related_to_disease': d_chemical.get(disease_id, {})
                                }
                           }
                else:
                    _doc = {'_id': _mondo,
                            'ctd': {
                                'omim': disease_id.split(':')[1],
                                'bp_related_to_disease': d_go_bp.get(disease_id, {}),
                                'mf_related_to_disease': d_go_mf.get(disease_id, {}),
                                'cc_related_to_disease': d_go_cc.get(disease_id, {}),
                                'pathway_related_to_disease': d_pathway.get(disease_id, {}),
                                'chemical_related_to_disease': d_chemical.get(disease_id, {})
                                }
                           }
                _doc = (dict_sweep(unlist(_doc), [None]))
                yield _doc
        else:
            if disease_id.startswith('MESH'):
                _doc = {'_id': disease_id,
                        'ctd': {
                            'mesh': disease_id.split(':')[1],
                            'bp_related_to_disease': d_go_bp.get(disease_id, {}),
                            'mf_related_to_disease': d_go_mf.get(disease_id, {}),
                            'cc_related_to_disease': d_go_cc.get(disease_id, {}),
                            'pathway_related_to_disease': d_pathway.get(disease_id, {}),
                            'chemical_related_to_disease': d_chemical.get(disease_id, {})
                            }
                       }
            else:
                _doc = {'_id': _mondo,
                        'ctd': {
                            'omim': disease_id.split(':')[1],
                            'bp_related_to_disease': d_go_bp.get(disease_id, {}),
                            'mf_related_to_disease': d_go_mf.get(disease_id, {}),
                            'cc_related_to_disease': d_go_cc.get(disease_id, {}),
                            'pathway_related_to_disease': d_pathway.get(disease_id, {}),
                            'chemical_related_to_disease': d_chemical.get(disease_id, {})
                            }
                       }
            _doc = (dict_sweep(unlist(_doc), [None]))
            yield _doc