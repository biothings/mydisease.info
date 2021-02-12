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
        mondo_docs = data["graphs"][0]["nodes"]
        for record in mondo_docs:
            if "id" in record and record["id"].startswith(
                "http://purl.obolibrary.org/obo/MONDO_"
            ):
                if "meta" in record and "xrefs" in record["meta"]:
                    for _xref in record["meta"]["xrefs"]:
                        prefix = _xref["val"].split(":")[0]
                        if prefix.lower() == "orphanet" or prefix.lower() == "omim":
                            mondo_id = "MONDO:" + record["id"].split("_")[-1]
                            umls_2_mondo[_xref["val"].upper()].append(mondo_id)
    return umls_2_mondo


def process_disease2hp(file_path_disease_hpo):
    df_disease_hpo = pd.read_csv(file_path_disease_hpo, sep="\t", skiprows=4, dtype=str)
    df_disease_hpo = df_disease_hpo.rename(
        index=str, columns={"DiseaseName": "disease_name", "#DatabaseID": "disease_id"}
    )
    
    ## removing qualifier = 'NOT' annotations, because it means the disease does not
    ##   have this phenotypic feature. The HPO website doesn't show these 'NOT' annots
    df_disease_hpo = df_disease_hpo[df_disease_hpo['Qualifier'] != "NOT"]
    ## then remove the qualifier
    df_disease_hpo.drop(columns = 'Qualifier', inplace = True)
    ## make sure all null values are None
    df_disease_hpo = df_disease_hpo.where((pd.notnull(df_disease_hpo)), None)
    
    d = []
    for did, subdf in df_disease_hpo.groupby("disease_id"):
        did = did.replace("ORPHA", "ORPHANET")
        records = subdf.to_dict(orient="records")
        
        pathway_related = []
        course = []
        modifiers = []
        inheritance = []
        
        for record in records:
            record_dict = {}
            if record["Aspect"] == "C":
                course.append(record["HPO_ID"])
                continue
            elif record["Aspect"] == "M":
                modifiers.append(record["HPO_ID"])
                continue
            elif record["Aspect"] == "I":
                inheritance.append(record["HPO_ID"])
                continue      
                
            for k, v in record.items():
                # name the field based on pathway database
                if (k == "Sex") and v:
                    record_dict['sex'] = v.lower()
                elif (k == 'Reference') and v: 
                ## only process if Reference has a value
                    ## this is a string representing a list
                    tempRefs = v.split(";")
                    ## prepare to iterate through the tempRefs and store the processed data
                    isbnL = []
                    pmidL = []
                    websiteL = []
                    for i in tempRefs:
                        if 'ISBN' in i:
                            isbnL.append(i.split(":")[1])
                        elif 'PMID:' in i:
                            pmidL.append(i[5:])
                        elif 'http' in i:
                            websiteL.append(i)
                        ## generate website URLs
                        elif 'DECIPHER:' in i:
                            websiteL.append(\
                                'https://decipher.sanger.ac.uk/syndrome/{0}/overview'.format(i[9:]))
                        elif 'OMIM:' in i:
                            websiteL.append(('https://www.omim.org/entry/' + i[5:]))  
                        elif 'ORPHA:' in i:
                            websiteL.append(\
                                'https://www.orpha.net/consor/cgi-bin/OC_Exp.php?lng=EN&Expert=' + i[6:])
                    ## ONLY add reference keys/values to the record if there are values
                    if isbnL:
                        record_dict['isbn_ref'] = isbnL
                    if pmidL:
                        record_dict['pmid_ref'] = pmidL                    
                    if websiteL:
                        record_dict['website_ref'] = websiteL
                elif (k == 'Frequency') and v:
                ## only process if Frequency has a value
                    tempDict = {}
                    if 'http' in v:  ## catching an error in the data
                        continue
                    elif 'HP:' in v:
                        tempDict['hp_freq'] = v
                    elif '%' in v:
                        tempFreq = float(v.strip('%')) / 100
                        ## only go forward if this is a valid fraction <=1
                        if tempFreq <= 1:
                            tempDict['numeric_freq'] = tempFreq
                    elif '/' in v:
                        ## idx 0 is numerator, idx 1 is denominator
                        tempL = [int(ele) for ele in v.split("/")]
                        ## only go forward if this is a valid fraction <=1
                        if (tempL[0] != 0) and (tempL[1] !=0) and (tempL[0] <= tempL[1]):
                            tempDict['freq_numerator'] = tempL[0]
                            tempDict['freq_denominator'] = tempL[1]
                            tempDict['numeric_freq'] = tempL[0] / tempL[1]

                    ## ONLY add frequency keys/values to the record if there are values
                    if tempDict:
                        record_dict.update(tempDict)
                        
                elif (k == 'Modifier') and v:
                ## only process if Modifier has a value
                    ## in <20 records, this is a delimited list with repeated values
                    ## this behavior matches the unlist behavior used with biothings APIs
                    ## https://github.com/kevinxin90/biothings.api/blob/master/biothings/utils/dataload.py
                    if ";" in v:
                        ## transform to list -> set->list to remove repeated values
                        tempMods = list(set(v.split(";")))
                        record_dict['modifier'] = tempMods
                    else:
                        record_dict['modifier'] = v
                elif k not in {"disease_id", "disease_name", 
                               "Aspect", "Sex", 
                               "Reference", "Frequency", 
                               "Modifier"}:
                    record_dict[k.lower()] = v
            pathway_related.append(record_dict)
        drecord = {
            "_id": did,
            "hpo": pathway_related,
            "disease_name": records[0]["disease_name"],
            "course": course,
            "modifiers": modifiers,
            "inheritance": inheritance
        }
        d.append(drecord)
 
    return {
        x["_id"]: [x["hpo"], x["disease_name"], x["course"], x["modifiers"], x["inheritance"]] for x in d
    }


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
    file_path_disease_hpo = os.path.join(data_folder, "phenotype.hpoa")
    file_path_mondo = os.path.join(data_folder, "mondo.json")
    d_hpo = process_disease2hp(file_path_disease_hpo)
    orphanet_omim_2_mondo = construct_orphanet_omim_to_mondo_library(file_path_mondo)
    for disease_id in d_hpo.keys():
        # for disease_id in set(list(d_go_bp.keys()) + list(d_go_mf.keys()) + list(d_go_cc.keys()) + list(d_pathway.keys())):
        if disease_id in orphanet_omim_2_mondo:
            mondo_id = orphanet_omim_2_mondo[disease_id]
            for _mondo in mondo_id:
                if disease_id.startswith("OMIM"):
                    _doc = {
                        "_id": _mondo,
                        "hpo": {
                            "disease_name": d_hpo.get(disease_id, {})[1],
                            "omim": disease_id.split(":")[1],
                            "phenotype_related_to_disease": d_hpo.get(disease_id, {})[
                                0
                            ],
                            "course": d_hpo.get(disease_id, {})[2],
                            "modifier": d_hpo.get(disease_id, {})[3],
                            "inheritance": d_hpo.get(disease_id, {})[4],
                        },
                    }
                elif disease_id.startswith("ORPHANET"):
                    _doc = {
                        "_id": _mondo,
                        "hpo": {
                            "disease_name": d_hpo.get(disease_id, {})[1],
                            "orphanet": disease_id.split(":")[1],
                            "phenotype_related_to_disease": d_hpo.get(disease_id, {})[
                                0
                            ],
                            "course": d_hpo.get(disease_id, {})[2],
                            "modifier": d_hpo.get(disease_id, {})[3],
                            "inheritance": d_hpo.get(disease_id, {})[4],
                        },
                    }
                else:
                    print(disease_id)
                _doc = dict_sweep(unlist(_doc), [None])
                yield _doc

        else:
            if disease_id.startswith("OMIM"):
                _doc = {
                    "_id": disease_id,
                    "hpo": {
                        "disease_name": d_hpo.get(disease_id, {})[1],
                        "omim": disease_id.split(":")[1],
                        "phenotype_related_to_disease": d_hpo.get(disease_id, {})[0],
                        "course": d_hpo.get(disease_id, {})[2],
                        "modifier": d_hpo.get(disease_id, {})[3],
                        "inheritance": d_hpo.get(disease_id, {})[4],

                    },
                }
            elif disease_id.startswith("ORPHANET"):
                _doc = {
                    "_id": disease_id,
                    "hpo": {
                        "disease_name": d_hpo.get(disease_id, {})[1],
                        "orphanet": disease_id.split(":")[1],
                        "phenotype_related_to_disease": d_hpo.get(disease_id, {})[0],
                        "course": d_hpo.get(disease_id, {})[2],
                        "modifier": d_hpo.get(disease_id, {})[3],
                        "inheritance": d_hpo.get(disease_id, {})[4],
                    },
                }
            else:
                _doc = {
                    "_id": disease_id,
                    "hpo": {
                        "disease_name": d_hpo.get(disease_id, {})[1],
                        "decipher": disease_id.split(":")[1],
                        "phenotype_related_to_disease": d_hpo.get(disease_id, {})[0],
                        "course": d_hpo.get(disease_id, {})[2],
                        "modifier": d_hpo.get(disease_id, {})[3],
                        "inheritance": d_hpo.get(disease_id, {})[4],
                    },
                }
            _doc = dict_sweep(unlist(_doc), [None])
            yield _doc