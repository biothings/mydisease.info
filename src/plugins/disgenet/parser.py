import json
import os
from collections import defaultdict

import numpy as np
import pandas as pd
from biothings.utils.dataload import dict_sweep, unlist

# LEGACY CODE
# Due to disgenet becoming a paid service, the following code is no longer functional. See the blog post for more information.
# The last release for this plugin was May 2024. The following code is kept for reference purposes only.


####################################################################################################################
# The source data contains two files:
# File 1: https://www.disgenet.org/static/disgenet_ap1/files/downloads/all_gene_disease_pmid_associations.tsv.gz
#         This file contain all gene-disease associations in DisGeNET, with one row per source and pubmed.
#         The file includes data from both curated sources (e.g. UNIPROT, CTD) as well as auto extracted
#         ones (e.g. BeFree). We will change the data structure to merge pubmed values (when all other row
#         values are the same.
# File 2: https://www.disgenet.org/static/disgenet_ap1/files/downloads/all_variant_disease_pmid_associations.tsv.gz
#         This file contain all variant-disease associations in DisGeNET, with one row per source and pubmed.
#         The file includes data from both curated sources (e.g. UNIPROT, GWASCAT) as well as auto extracted
#         ones (e.g. BeFree). We will change the data structure to merge pubmed values (when all other row
#         values are the same.
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
#             "DPI": ####,
#             "DSI": ####,
#             "EI": ####,
#             "YearFinal": ####,
#             "YearInitial": ####,
#             "gene_id": ####,
#             "gene_name": "####",
#             "pubmed": [####],
#             "score": ####,
#             "source": "####"
#        },
#        "variants_related_to_disease": {
#             "DPI": ####,
#             "DSI": ####,
#             "EI": ####,
#             "YearFinal": ####,
#             "YearInitial": ####,
#             "chrom": "####",
#             "pos": ####,
#             "pubmed": [####],
#             "rsid": "####",
#             "score": ####,
#             "source": "###"
#        }
#    }
# }
##############################################################################################

def to_list(col):
    new_col = []
    for _row in col:
        _row = _row.split(";")
        if _row and len(_row) == 1:
            new_col.append(_row[0])
        else:
            new_col.append(_row)
    return new_col


def process_gene(file_path_gene_disease):
    df_gene_disease = pd.read_csv(
        file_path_gene_disease,
        encoding="ISO-8859-1",
        sep="\t",
        comment="#",
        # compression="gzip",
        compression="infer",
    )
    rename_gene = {
        "diseaseId": "umls",
        "geneId": "gene_id",
        "geneSymbol": "gene_name",
        "diseaseName": "disease_name",
        "pmid": "pubmed",
    }
    df_gene_disease = df_gene_disease.where(
        (pd.notnull(df_gene_disease)), None)
    # source field could be multiple data sources concatenated by ";", break them into a list
    # df_gene_disease.source = to_list(df_gene_disease.source)
    # df_gene_disease.diseaseType = to_list(df_gene_disease.diseaseType)
    # df_gene_disease.diseaseSemanticType = to_list(df_gene_disease.diseaseSemanticType)
    d = defaultdict(list)
    # rename pandas columns
    df_gene_disease = df_gene_disease.rename(columns=rename_gene)
    # for each gene, group the results based on source, and merge all pubmed IDs together
    for grp, subdf in df_gene_disease.groupby(["umls", "source", "gene_id"]):
        records = subdf.to_dict(orient="records")
        doc = {"source": grp[1], "gene_id": int(grp[2]), "pubmed": set()}
        for record in records:
            for k, v in record.items():
                if pd.isna(v):
                    v = None
                if isinstance(v, np.int64):
                    record[k] = int(v)
                if k in ["gene_name", "DSI", "DPI", "score", "EI"]:
                    doc[k] = v
                elif k in ["YearInitial", "YearFinal"]:
                    doc[k] = int(v) if v else v
                elif k == "pubmed" and v:
                    doc[k].add(int(v))
        doc["pubmed"] = list(doc["pubmed"])
        d[grp[0].replace("umls", "umls_cui")].append(doc)
    return d


def process_snp(file_path_snp_disease):
    df_snp = pd.read_csv(
        file_path_snp_disease, sep="\t", comment="#", compression="gzip"
    )
    rename_variant = {
        "diseaseId": "umls",
        "diseaseName": "disease_name",
        #         "originalSource": "source",
        "pmid": "pubmed",
        "snpId": "rsid",
        "chromosome": "chrom",
        "position": "pos",
        "diseaseType": "disease_type",
        #         "originalSource": "source",
        #         "sentence": "description",
    }
    # rename columns
    df_snp = df_snp.rename(columns=rename_variant)
    # change nan values to none
    df_snp = df_snp.where((pd.notnull(df_snp)), None)
    # source field could be multiple data sources concatenated by ";", break them into a list
#     source_col = df_snp.source
#     new_source_col = []
#     for _row in source_col:
#         _row = _row.split(";")
#         if _row and len(_row) == 1:
#             new_source_col.append(_row[0])
#         else:
#             new_source_col.append(_row)
#     df_snp.source = new_source_col
    d = defaultdict(list)
    # rename pandas columns
    # for each gene, group the results based on source, and merge all pubmed IDs together
    for grp, subdf in df_snp.groupby(["umls", "source", "rsid"]):
        records = subdf.to_dict(orient="records")
        doc = {"source": grp[1], "rsid": grp[2], "pubmed": set()}
        for record in records:
            for k, v in record.items():
                if pd.isna(v):
                    v = None
                if isinstance(v, np.int64):
                    record[k] = int(v)
                if k in ["chrom", "DSI", "DPI", "score", "EI"]:
                    doc[k] = v
                elif k in ["YearInitial", "YearFinal", "pos"]:
                    doc[k] = int(v) if v else v
                elif k == "pubmed" and v:
                    doc[k].add(int(v))
        doc["pubmed"] = list(doc["pubmed"])
        d[grp[0].replace("umls", "umls_cui")].append(doc)
    return d


def process_xrefs(file_path_disease_mapping):
    df_disease_mapping = pd.read_csv(
        file_path_disease_mapping, sep="\t", comment="#", compression="gzip"
    )
    d = []
    for did, subdf in df_disease_mapping.groupby("diseaseId"):
        records = subdf.to_dict(orient="records")
        drecord = {
            "_id": did.replace("umls", "umls_cui"),
            "xrefs": {
                "umls": did.replace("umls", "umls_cui"),
                "disease_name": records[0]["name"],
            },
        }
        for _record in records:
            for k, v in _record.items():
                if isinstance(v, np.int64):
                    _record[k] = int(v)
            drecord["xrefs"][
                _record["vocabulary"]
                .lower()
                .replace("msh", "mesh")
                .replace("do", "doid")
                .replace("ordoid", "ordo")
                .replace("hpo", "hp")
                .replace("icd9cm", "icd9")
                .replace("mondoid", "mondo")
            ] = _record["code"]
            if _record["vocabulary"].lower() == "do":
                drecord["xrefs"]["doid"] = "DOID:" + str(_record["code"])
            if _record["vocabulary"].lower() == "efo":
                drecord["xrefs"]["efo"] = "EFO:" + str(_record["code"])
            if _record["vocabulary"].lower() == "mondo":
                drecord["xrefs"]["mondo"] = "MONDO:" + str(_record["code"])
        d.append(drecord)
    return {x["_id"]: x["xrefs"] for x in d}


# Build a dictionary to map from UMLS identifier to MONDO ID
def construct_umls_to_mondo_library(file_path_mondo):
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
                        if prefix.lower() == "umls":
                            mondo_id = "MONDO:" + record["id"].split("_")[-1]
                            umls_2_mondo[_xref["val"][len(prefix) + 1:]].append(
                                mondo_id
                            )
    return umls_2_mondo


def load_data(data_folder):
    file_path_mondo = os.path.join(data_folder, "mondo.json")
    file_path_gene_disease = os.path.join(
        # data_folder, "all_gene_disease_pmid_associations.tsv.gz"
        data_folder, "filtered_gene_disease_associations.tsv"
    )
    file_path_snp_disease = os.path.join(
        data_folder, "all_variant_disease_pmid_associations.tsv.gz"
    )
    file_path_disease_mapping = os.path.join(
        data_folder, "disease_mappings.tsv.gz")
    d_gene = process_gene(file_path_gene_disease)
    d_snp = process_snp(file_path_snp_disease)
    d_xrefs = process_xrefs(file_path_disease_mapping)
    umls_2_mondo = construct_umls_to_mondo_library(file_path_mondo)
    for umls_id in set(list(d_gene.keys()) + list(d_snp.keys())):
        if umls_id in d_xrefs and "mondo" in d_xrefs[umls_id]:
            _doc = {
                "_id": d_xrefs[umls_id]["mondo"],
                "disgenet": {
                    "xrefs": d_xrefs.get(umls_id, {}),
                    "genes_related_to_disease": d_gene.get(umls_id, {}),
                    "variants_related_to_disease": d_snp.get(umls_id, {}),
                },
            }
            _doc = dict_sweep(unlist(_doc), [None])
            yield _doc
        elif umls_id in umls_2_mondo:
            mondo_id = umls_2_mondo[umls_id]
            for _mondo in mondo_id:
                _doc = {
                    "_id": _mondo,
                    "disgenet": {
                        "xrefs": d_xrefs.get(umls_id, {}),
                        "genes_related_to_disease": d_gene.get(umls_id, {}),
                        "variants_related_to_disease": d_snp.get(umls_id, {}),
                    },
                }
                _doc = dict_sweep(unlist(_doc), [None])
                yield _doc
        else:
            _doc = {
                "_id": umls_id,
                "disgenet": {
                    "xrefs": d_xrefs.get(umls_id, {}),
                    "genes_related_to_disease": d_gene.get(umls_id, {}),
                    "variants_related_to_disease": d_snp.get(umls_id, {}),
                },
            }
            _doc = dict_sweep(unlist(_doc), [None])
            yield _doc
