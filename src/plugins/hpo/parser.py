import json
import os
from collections import defaultdict

import pandas as pd
from biothings.utils.dataload import dict_sweep, unlist


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
    df_disease_hpo = pd.read_csv(
        file_path_disease_hpo, sep="\t", skiprows=4, dtype=str)
    df_disease_hpo = df_disease_hpo.rename(
        index=str, columns={"database_id": "disease_id"}
    )
    # removing qualifier = 'NOT' annotations, because it means the disease does not
    # have this phenotypic feature. The HPO website doesn't show these 'NOT' annots
    df_disease_hpo = df_disease_hpo[df_disease_hpo['qualifier'] != "NOT"]
    # then remove the qualifier
    df_disease_hpo.drop(columns='qualifier', inplace=True)
    # make sure all null values are None
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
            if record["aspect"] == "C":
                course.append(record["hpo_id"])
                continue
            elif record["aspect"] == "M":
                modifiers.append(record["hpo_id"])
                continue
            elif record["aspect"] == "I":
                inheritance.append(record["hpo_id"])
                continue
            for k, v in record.items():
                # name the field based on pathway database
                if (k == "sex") and v:
                    record_dict['sex'] = v.lower()
                elif (k == 'reference') and v:
                    # only process if Reference has a value
                    # notes: OMIM:194190, OMIM:180849, OMIM:212050 are disease examples with > 1 type of reference
                    # this is a string representing a list
                    tempRefs = v.split(";")
                    # prepare to iterate through the tempRefs and store the processed data
                    tempProperties = {
                        'ISBN': [],
                        'PMID': [],
                        'http': [],
                        'DECIPHER': [],
                        'OMIM': [],
                        'ORPHA': []
                    }
                    # remove the prefixes or not? currently keeping the prefix
                    for i in tempRefs:
                        for key in tempProperties.keys():
                            if key in i:
                                # replace curie prefix for isbn and orpha
                                if key == 'ISBN':
                                    tempProperties[key].append(
                                        'ISBN:' + i.split(":")[1])
                                elif key == 'ORPHA':
                                    tempProperties[key].append(
                                        'ORPHANET:' + i.split(":")[1])
                                else:
                                    tempProperties[key].append(i)
                    # ONLY add reference keys/values to the record if there are values
                    for k, v in tempProperties.items():
                        if v:
                            if k == 'ISBN':
                                record_dict['isbn_refs'] = v
                            elif k == 'PMID':
                                record_dict['pmid_refs'] = v
                            elif k == 'http':
                                record_dict['website_refs'] = v
                            elif k == 'DECIPHER':
                                record_dict['decipher_refs'] = v
                            elif k == 'OMIM':
                                record_dict['omim_refs'] = v
                            elif k == 'ORPHA':
                                record_dict['orphanet_refs'] = v
                elif (k == 'frequency') and v:
                    # only process if frequency has a value
                    tempDict = {}
                    if 'http' in v:  # catching an error in the data
                        continue
                    elif 'HP:' in v:
                        tempDict['hp_freq'] = v
                    elif '%' in v:
                        tempFreq = float(v.strip('%')) / 100
                        # only go forward if this is a valid fraction <=1
                        if tempFreq <= 1:
                            tempDict['numeric_freq'] = tempFreq
                    elif '/' in v:
                        # idx 0 is numerator, idx 1 is denominator
                        tempL = [int(ele) for ele in v.split("/")]
                        # only go forward if this is a valid fraction <=1
                        if (tempL[0] != 0) and (tempL[1] != 0) and (tempL[0] <= tempL[1]):
                            tempDict['freq_numerator'] = tempL[0]
                            tempDict['freq_denominator'] = tempL[1]
                            tempDict['numeric_freq'] = tempL[0] / tempL[1]
                    # ONLY add frequency keys/values to the record if there are values
                    if tempDict:
                        record_dict.update(tempDict)
                elif (k == 'modifier') and v:
                    # only process if modifier has a value
                    # in <20 records, this is a delimited list with repeated values
                    # this behavior matches the unlist behavior used with biothings APIs
                    # https://github.com/kevinxin90/biothings.api/blob/master/biothings/utils/dataload.py
                    if ";" in v:
                        # transform to list -> set->list to remove repeated values
                        tempMods = list(set(v.split(";")))
                        record_dict['modifier'] = tempMods
                    else:
                        record_dict['modifier'] = v
                elif k not in {"disease_id", "disease_name",
                               "aspect", "sex",
                               "reference", "frequency",
                               "modifier"}:
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
    orphanet_omim_2_mondo = construct_orphanet_omim_to_mondo_library(
        file_path_mondo)

    aggregated_data = {}

    # First, aggregate data by MONDO ID, incorporating all source IDs
    for disease_id, annotations in d_hpo.items():
        mondo_ids = orphanet_omim_2_mondo.get(disease_id, [disease_id])

        for mondo_id in mondo_ids:
            if mondo_id not in aggregated_data:
                aggregated_data[mondo_id] = []

            annotations_with_source = annotations.copy()
            # Include source ID in annotations
            annotations_with_source["source_id"] = disease_id
            aggregated_data[mondo_id].append(annotations_with_source)

    # Then, process aggregated data to yield documents
    for mondo_id, annotations_list in aggregated_data.items():
        # Create a unified document structure that accommodates all annotations
        _doc = {
            "_id": mondo_id,
            "hpo": []
        }

        # Iterate through annotations from different sources
        for annotations in annotations_list:
            # Remove the source ID from the annotations
            source_id = annotations.pop("source_id")

            # Depending on the source, you might adjust how you add annotations to _doc
            if source_id.startswith("OMIM"):
                annotations["source"] = "OMIM"
            elif source_id.startswith("ORPHANET"):
                annotations["source"] = "Orphanet"
            elif source_id.startswith("DECIPHER"):
                annotations["source"] = "Decipher"

            # Add the annotations to the document
            _doc["hpo"].append(annotations)

        # Ensure _doc is properly cleaned up (e.g., removing lists with only one item, handling None values)
        _doc_cleaned = dict_sweep(unlist(_doc), [None])
        yield _doc_cleaned
