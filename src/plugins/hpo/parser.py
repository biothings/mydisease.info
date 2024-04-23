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


def unique_biocuration(biocurations):
    unique_list = []
    seen = set()
    for biocuration in biocurations:
        identifier = tuple(biocuration.items())
        if identifier not in seen:
            seen.add(identifier)
            unique_list.append(biocuration)
    return unique_list


def biocuration_parser(biocuration_string):
    # Convert the biocuration string to a list of dictionaries. Example: HPO:skoehler[2010-04-21];HPO:lcarmody[2019-06-02] -> [{'name': 'skoehler', 'date': '2010-04-21'}, {'name': 'lcarmody', 'date': '2019-06-02'}]
    entries = biocuration_string.split(';')
    processed_entries = []
    for entry in entries:
        name, date_with_brackets = entry.split('[')
        date = date_with_brackets[:-1]
        processed_entries.append({'name': name, 'date': date})
    return processed_entries


def process_frequency(frequency):
    # only process if frequency has a value
    tempDict = {}

    # Skip processing if the frequency value is empty
    if not frequency:
        return None

    # catching an error in the data
    if 'http' in frequency:
        return None

    # Process based on the format of the frequency value
    if 'HP:' in frequency:
        tempDict['hp_freq'] = frequency
    elif '%' in frequency:
        # only go forward if this is a valid fraction <=1
        tempFreq = float(frequency.strip('%')) / 100
        if tempFreq <= 1:
            tempDict['numeric_freq'] = tempFreq
    elif '/' in frequency:
        # idx 0 is numerator, idx 1 is denominator
        tempL = [int(ele) for ele in frequency.split("/")]
        # only go forward if this is a valid fraction <=1
        if (tempL[0] != 0) and (tempL[1] != 0) and (tempL[0] <= tempL[1]):
            tempDict['freq_numerator'] = tempL[0]
            tempDict['freq_denominator'] = tempL[1]
            tempDict['numeric_freq'] = tempL[0] / tempL[1]

    return tempDict


def create_aspect_dict(record, hpo_lookup, biocuration_parser, did):
    aspect_dict = {}
    aspect_dict['hpo_id'] = record["hpo_id"]
    aspect_dict['hpo_name'] = hpo_lookup[record["hpo_id"]]
    aspect_dict['evidence'] = record["evidence"]
    biocuration = biocuration_parser(record['biocuration'])
    if biocuration:
        aspect_dict['biocuration'] = unique_biocuration(biocuration)
    aspect_dict['original_disease_id'] = did

    references = record["reference"].split(
        ";") if "reference" in record else []
    aspect_dict['pmid_refs'] = [ref for ref in references if "PMID" in ref]
    aspect_dict['omim_refs'] = [ref for ref in references if "OMIM" in ref]
    aspect_dict['orphanet_refs'] = [
        ref for ref in references if "ORPHA" in ref]
    aspect_dict['isbn_refs'] = [ref for ref in references if "ISBN" in ref]
    aspect_dict['website_refs'] = [ref for ref in references if "http" in ref]
    aspect_dict['decipher_refs'] = [
        ref for ref in references if "DECIPHER" in ref]

    frequency = process_frequency(record.get('frequency', ''))
    if frequency:
        aspect_dict.update(frequency)

    return aspect_dict


def create_hpo_lookup(file_path_hpo):
    with open(file_path_hpo) as f:
        data = json.load(f)

    # Extract the list of nodes, each representing an HPO term
    hpo_docs = data["graphs"][0]["nodes"]

    lookup_dict = {}

    for doc in hpo_docs:
        hpo_id = doc.get('id')
        hpo_id = hpo_id.replace("http://purl.obolibrary.org/obo/HP_", "HP:")
        hpo_name = doc.get('lbl')  # Get the HPO name (label)

        if hpo_id and hpo_name:
            lookup_dict[hpo_id] = hpo_name

    return lookup_dict


def process_disease2hp(file_path_disease_hpo, hpo_lookup):
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
        # Replace ORPHA:79414 with ORPHANET:79414 to match the mondo mapping
        did = did.replace("ORPHA", "ORPHANET")
        records = subdf.to_dict(orient="records")
        pathway_related = []
        # Changed course to clinical_course, modifier to clinical_modifier to match the source
        # https://hpo-annotation-qc.readthedocs.io/en/latest/annotationFormat.html#phenotype-hpoa-format
        clinical_course = []
        clinical_modifier = []
        inheritance = []
        for record in records:
            record_dict = {}
            if record["aspect"] == "C":
                clinical_course_dict = create_aspect_dict(
                    record, hpo_lookup, biocuration_parser, did)
                clinical_course.append(clinical_course_dict)
                continue
            elif record["aspect"] == "M":
                clinical_modifier_dict = create_aspect_dict(
                    record, hpo_lookup, biocuration_parser, did)
                clinical_modifier.append(clinical_modifier_dict)
                continue
            elif record["aspect"] == "I":
                inheritance_dict = create_aspect_dict(
                    record, hpo_lookup, biocuration_parser, did)
                inheritance.append(inheritance_dict)
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
                    result = process_frequency(v)
                    if result:
                        record_dict.update(result)
                elif (k == 'modifier') and v:
                    # only process if modifier has a value
                    # in <20 records, this is a delimited list with repeated values
                    # this behavior matches the unlist behavior used with biothings APIs
                    # https://github.com/kevinxin90/biothings.api/blob/master/biothings/utils/dataload.py
                    if ";" in v:
                        # transform to list -> set->list to remove repeated values
                        tempMods = list(set(v.split(";")))
                        # TODO change to clinical_modifier, check if this is the same definition of modifier
                        record_dict['clinical_modifier'] = tempMods
                    else:
                        record_dict['clinical_modifier'] = v
                elif (k == 'biocuration') and v:
                    processed_entries = biocuration_parser(v)
                    record_dict['biocuration'] = processed_entries
                elif k not in {"disease_id", "disease_name",
                               "aspect", "sex",
                               "reference", "frequency",
                               "clinical_modifier"}:
                    record_dict[k.lower()] = v
            pathway_related.append(record_dict)
        drecord = {
            "_id": did,
            "hpo": pathway_related,
            "disease_name": records[0]["disease_name"],
            "clinical_course": clinical_course,
            "clinical_modifier": clinical_modifier,
            "inheritance": inheritance
        }
        d.append(drecord)
    return {
        x["_id"]: [x["hpo"], x["disease_name"], x["clinical_course"], x["clinical_modifier"], x["inheritance"]] for x in d
    }


def merge_phenotypes(existing_phenotypes, new_phenotypes):
    if isinstance(existing_phenotypes, dict):
        existing_phenotypes = [existing_phenotypes]
    if isinstance(new_phenotypes, dict):
        new_phenotypes = [new_phenotypes]

    merged_phenotypes = existing_phenotypes + new_phenotypes
    return merged_phenotypes


def load_data(data_folder):
    file_path_disease_hpo = os.path.join(data_folder, "phenotype.hpoa")
    file_path_mondo = os.path.join(data_folder, "mondo.json")
    file_path_hpo = os.path.join(data_folder, "hp.json")
    hpo_lookup = create_hpo_lookup(file_path_hpo)
    d_hpo = process_disease2hp(file_path_disease_hpo, hpo_lookup)
    orphanet_omim_2_mondo = construct_orphanet_omim_to_mondo_library(
        file_path_mondo)

    documents = {}  # Dictionary to track documents by MONDO ID

    for disease_id, hpo_info in d_hpo.items():
        if disease_id in orphanet_omim_2_mondo:
            mondo_ids = orphanet_omim_2_mondo[disease_id]
            for _mondo in mondo_ids:
                if _mondo not in documents:
                    documents[_mondo] = {
                        "_id": _mondo,
                        "hpo": {
                            "disease_name": hpo_info[1],
                            "phenotype_related_to_disease": [],
                            "clinical_course": [],
                            "clinical_modifier": [],
                            "inheritance": [],
                            "omim": [],
                            "orphanet": [],
                        },
                    }

                _doc = documents[_mondo]
                _doc_hpo = _doc["hpo"]

                # Possible to have multiple OMIM and Orphanet IDs, see MONDO:0030914
                if disease_id.startswith("OMIM"):
                    omim_id = disease_id.split(":")[1]
                    if omim_id not in _doc_hpo["omim"]:
                        _doc_hpo["omim"].append(omim_id)
                elif disease_id.startswith("ORPHANET"):
                    orphanet_id = disease_id.split(":")[1]
                    if orphanet_id not in _doc_hpo["orphanet"]:
                        _doc_hpo["orphanet"].append(orphanet_id)

                # Merge the phenotype_related_to_disease lists
                existing_phenotypes = _doc_hpo["phenotype_related_to_disease"]
                new_phenotypes = hpo_info[0]

                # If new_phenotypes is a single dict, wrap it in a list
                if isinstance(new_phenotypes, dict):
                    new_phenotypes = [new_phenotypes]
                for phenotype in new_phenotypes:
                    source_prefix, source_id = disease_id.split(":")

                    if source_prefix.upper() == "ORPHA":
                        source_prefix = "ORPHANET"

                    full_source_id = f"{source_prefix}:{source_id}"

                    phenotype['original_disease_id'] = full_source_id

                    if phenotype not in existing_phenotypes:
                        existing_phenotypes.append(phenotype)

                # Merge lists for "clinical_course", "clinical_modifier", and "inheritance"
                for field, index in zip(["clinical_course", "clinical_modifier", "inheritance"], [2, 3, 4]):
                    existing_list = _doc_hpo.get(field, [])
                    new_items = hpo_info[index]
                    existing_list.extend(new_items)
                    _doc_hpo[field] = existing_list
                documents[_mondo] = _doc

        else:
            if disease_id.startswith("OMIM"):
                _doc = {
                    "_id": disease_id,
                    "hpo": {
                        "disease_name": d_hpo.get(disease_id, {})[1],
                        "omim": disease_id.split(":")[1],
                        "phenotype_related_to_disease": d_hpo.get(disease_id, {})[0],
                        "clinical_course": d_hpo.get(disease_id, {})[2],
                        "clinical_modifier": d_hpo.get(disease_id, {})[3],
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
                        "clinical_course": d_hpo.get(disease_id, {})[2],
                        "clinical_modifier": d_hpo.get(disease_id, {})[3],
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
                        "clinical_course": d_hpo.get(disease_id, {})[2],
                        "clinical_modifier": d_hpo.get(disease_id, {})[3],
                        "inheritance": d_hpo.get(disease_id, {})[4],
                    },
                }
            _doc = dict_sweep(unlist(_doc), [None])
            yield _doc

    for _doc in documents.values():
        _doc = dict_sweep(unlist(_doc), [None])
        yield _doc
