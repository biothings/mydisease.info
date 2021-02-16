from collections import defaultdict
from biothings.utils.dataload import dict_sweep, unlist
import pandas as pd
import json
import os


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

def process_pathway(file_path_pathway):
    # read in the data frame
    df_disease_pathway = pd.read_csv(file_path_pathway, sep=',', comment='#', compression='gzip',
                                     names=['DiseaseName', 'DiseaseID', 'pathway_name', 'pathway_id', 'inference_gene_symbol'],
                                     dtype=str)
    d = {}
    ## going to merge records with the same disease - pathway (but different inference_gene_symbol values)
    for grp, subdf in df_disease_pathway.groupby(['DiseaseID', 'pathway_id']):
        ## make a new record        
        record_dict = {
            'source': 'CTD',
            'pathway_name': subdf['pathway_name'].tolist()[0]}
        ## name the field based on pathway database
        tempPathwayID = grp[1].split(':')
        record_dict[tempPathwayID[0].lower() + '_pathway_id'] = tempPathwayID[1] 
        ## get the inference gene symbol list
        tempGeneL = subdf['inference_gene_symbol'].unique().tolist()
        if len(tempGeneL) == 1:
            record_dict['inference_gene_symbol'] = tempGeneL[0]
        else:
            record_dict['inference_gene_symbol'] = tempGeneL
        ## if disease key already exists in d
        if d.get(grp[0]):
            d[grp[0]].append(record_dict)
        else:
            d[grp[0]] = [record_dict]
        ## note: <20 diseases have >1000 unique pathways linked to them
    return d

def process_chemical(file_path_chemical):
    chunksize = 100000
    d = []
    for chunk in pd.read_csv(file_path_chemical, chunksize=chunksize, sep=',', comment='#', compression='gzip', 
                             names=['chemical_name', 'mesh_chemical_id', 'cas_registry_number', 'DiseaseName', 'DiseaseID', 'direct_evidence', 'inference_gene_symbol', 'inference_score', 'omim_id', 'pubmed'],
                             dtype=str):
        temp_chunk = chunk.copy()
        temp_chunk = temp_chunk.where((pd.notnull(temp_chunk)), None)
        ## remove all inferred annotations
        ## there will be <5 disease keys with >1000 chemicals annotated to them
        temp_chunk = temp_chunk[~ temp_chunk['direct_evidence'].isna()]
        ## only work with records if the dataframe still has records 
        if not temp_chunk.empty: 
            ## make this the correct type
            temp_chunk['inference_score'] = temp_chunk['inference_score'].astype(float)
            temp_chunk = temp_chunk.where((pd.notnull(temp_chunk)), None)
            # add new column called source
            temp_chunk['source'] = 'CTD'         
            # the record in these fields are separated by '|', need to convert them into list
            for field_id in ['omim_id', 'pubmed']:
                temp_chunk[field_id] = temp_chunk[field_id].apply(lambda x: x.split('|') if x and '|' in x else x)
            for did, subdf in temp_chunk.groupby('DiseaseID'):
                records = subdf.to_dict(orient='records')
                chemical_related = [{k: v for k, v in record.items() if k not in {'DiseaseName', 'DiseaseID'}} for record in records]            
                drecord = {'_id': did, 'chemical': chemical_related}
                d.append(drecord)
    finalDict = {}
    ## For now, I'm not merging records. Current data situation is separate records when relationship is marker/mechanism AND therapeutic
    for ele in d:
        tempID = ele['_id']
        ## if an entry for this disease already exists in the dictionary
        if tempID in finalDict.keys():
            finalDict[tempID] = finalDict[tempID] + ele['chemical']
        else:
            finalDict[tempID] = ele['chemical']
    return finalDict

# def calculate_mondo_mismatch():
#     d_go_bp = process_go(file_path_disease_go_bp)
#     d_go_mf = process_go(file_path_disease_go_mf)
#     d_go_cc = process_go(file_path_disease_go_cc)
#     d_pathway = process_pathway(file_path_disease_pathway)
#     mesh_omim_2_mondo = construct_mesh_omim_to_mondo_library(file_path_mondo)
#     matched = []
#     mismatched = []
#     for disease_id in set(list(d_go_bp.keys()) + list(d_go_mf.keys()) + list(d_go_cc.keys()) + list(d_pathway.keys())):
#         if disease_id in mesh_omim_2_mondo:
#             matched.append(disease_id)
#         else:
#             mismatched.append(disease_id)
#     return {'matched': matched, 'mismatch': mismatched}

def load_data(data_folder):
    file_path_disease_pathway = os.path.join(data_folder, 'CTD_diseases_pathways.csv.gz')
    file_path_disease_chemical = os.path.join(data_folder, 'CTD_chemicals_diseases.csv.gz')
    file_path_mondo = os.path.join(data_folder, 'mondo.json')
    d_pathway = process_pathway(file_path_disease_pathway)
    print('loaded pathway data')
    d_chemical = process_chemical(file_path_disease_chemical)
    print('loaded chemical data')
    mesh_omim_2_mondo = construct_mesh_omim_to_mondo_library(file_path_mondo)
    for disease_id in set(list(d_pathway.keys()) + list(d_chemical.keys())):
    #for disease_id in set(list(d_go_bp.keys()) + list(d_go_mf.keys()) + list(d_go_cc.keys()) + list(d_pathway.keys())):
        if disease_id in mesh_omim_2_mondo:
            mondo_id = mesh_omim_2_mondo[disease_id]
            for _mondo in mondo_id:
                if disease_id.startswith('MESH'):
                    _doc = {'_id': _mondo,
                            'ctd': {
                                'mesh': disease_id.split(':')[1],
                                'pathway_related_to_disease': d_pathway.get(disease_id, {}),
                                'chemical_related_to_disease': d_chemical.get(disease_id, {})
                                }
                           }
                else:
                    _doc = {'_id': _mondo,
                            'ctd': {
                                'omim': disease_id.split(':')[1],
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
                            'pathway_related_to_disease': d_pathway.get(disease_id, {}),
                            'chemical_related_to_disease': d_chemical.get(disease_id, {})
                            }
                       }
            else:
                _doc = {'_id': disease_id,
                        'ctd': {
                            'omim': disease_id.split(':')[1],
                            'pathway_related_to_disease': d_pathway.get(disease_id, {}),
                            'chemical_related_to_disease': d_chemical.get(disease_id, {})
                            }
                       }
            _doc = (dict_sweep(unlist(_doc), [None]))
            yield _doc