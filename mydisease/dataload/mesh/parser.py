from collections import Counter
from collections import defaultdict
from itertools import groupby, filterfalse

import pandas as pd
from pymongo import MongoClient

from . import sem_groups_path, desc_path, supp_path


def load_semantic_types():
    # read in semantic types
    st_df = pd.read_csv(sem_groups_path, delimiter="|", names=["x0", "x1", "x2", "x3"])
    semantic_types = dict(zip(st_df['x2'], st_df['x3']))
    disorder_df = st_df.query("x1 == 'Disorders'")[['x2', 'x3']]
    disorders = set(disorder_df['x2'])
    return semantic_types, disorders


"""
Parse a Descriptor Record
all attributes listed here: https://www.nlm.nih.gov/mesh/dtype.html
# TODO: parse PRINT ENTRY and ENTRY completely
# "'D-2-hydroxyglutaric aciduria|T047|EQV|OMIM (2013)|ORD (2010)|090615|abdeef'"

Example record:

record = *NEWRECORD
RECTYPE = D
MH = Brain Diseases, Metabolic, Inborn
DE = BRAIN DIS METAB INBORN
AQ = BL CF CI CL CO DH DI DT EC EH EM EN EP ET GE HI IM ME MI MO NU PA PC PP PS PX RA RH RI RT SU TH UR US VE VI
PRINT ENTRY = Central Nervous System Inborn Metabolic Diseases|T047|NON|BRD|NLM (2000)|991012|CNS INBORN METAB DIS|abcdefv
PRINT ENTRY = Familial Metabolic Brain Diseases|T047|NON|NRW|NLM (2000)|991012|FAMILIAL METAB BRAIN DIS|abcdefv
ENTRY = Brain Diseases, Metabolic, Familial|T047|NON|NRW|NLM (2000)|991012|BRAIN DIS METAB FAMILIAL|abcdefv
ENTRY = Brain Diseases, Metabolic, Inherited|T047|NON|NRW|NLM (2000)|991012|BRAIN DIS METAB INHERITED|abcdefv
MN = C10.228.140.163.100
MN = C16.320.565.189
MN = C18.452.132.100
MN = C18.452.648.189
FX = Intellectual Disability
MH_TH = NLM (2000)
ST = T047
AN = General, prefer specifics; DF: BRAIN DIS METAB INBORN
PI = Brain/metabolism (1968-1999)
PI = Hereditary Diseases (1968-1999)
MS = Brain disorders resulting from inborn metabolic errors, primarily from enzymatic defects which lead to substrate accumulation, product reduction, or increase in toxic metabolites through alternate pathways. The majority of these conditions are familial, however spontaneous mutation may also occur in utero.
PM = 2000
HN = 2000
MR = 20110705
DA = 19991103
DC = 1
DX = 20000101
UI = D020739
"""


def load_mesh_desc():
    semantic_types, disorders = load_semantic_types()

    # read in the mesh data
    with open(desc_path) as f:
        mesh_desc = [x.strip() for x in f.readlines()]

    # note, only care about disease related attributes.
    # for example, ignoring RN CAS REGISTRY/EC NUMBER/UNII CODE
    attributes = {'MH': "term",
                  'MN': "tree",
                  'FX': "see_also",
                  'ST': "semantic_type",  # see: https://semanticnetwork.nlm.nih.gov/download/SemGroups.txt
                  'MS': "note",
                  'MR': "last_updated",
                  'DC': "descriptor_class",
                  'UI': "_id",
                  'RECTYPE': "record_type",
                  'synonyms': "synonyms"}  # added by me from PRINT ENTRY & ENTRY

    # which attributes can have multiple values?
    gb = filterfalse(lambda x: x[0], groupby(mesh_desc, lambda x: x == "*NEWRECORD"))
    ds = []
    for gb_record in gb:
        record = list(gb_record[1])
        d = dict(Counter([line.split("=", 1)[0].strip() for line in record if "=" in line]))
        ds.append(d)
    df = pd.DataFrame(ds).fillna(0)
    list_attribs = set(df.columns[df.max() > 1])

    # split into records
    gb = filterfalse(lambda x: x[0], groupby(mesh_desc, lambda x: x == "*NEWRECORD"))

    mesh_terms = []
    for gb_record in gb:
        record = list(gb_record[1])
        d = defaultdict(list)
        for line in record:
            if "=" not in line:
                continue
            key = line.split("=", 1)[0].strip()
            value = line.split("=", 1)[1].strip()
            if key in list_attribs and key in attributes:
                d[attributes[key]].append(value)
            elif key in attributes and key not in {"PRINT ENTRY", "ENTRY"}:
                d[attributes[key]] = value
            elif key == "PRINT ENTRY":
                d['synonyms'].append(value.split("|", 1)[0])
            elif key == "ENTRY":
                d['synonyms'].append(value.split("|", 1)[0])

        if not (set(d['semantic_type']) & disorders):
            continue
        d['semantic_type_id'] = d['semantic_type']
        d['semantic_type'] = [semantic_types[c] for c in d['semantic_type']]
        d['_id'] = "mesh:" + d['_id']
        mesh_terms.append(dict(d))
    return mesh_terms


"""
# Parse a Supplemental Record
# all attributes listed here: https://www.nlm.nih.gov/mesh/ctype.html
# 
# Example record:
record = *NEWRECORD
RECTYPE = C
NM = 2-Hydroxyglutaricaciduria
RN = 0
SY = 2-Hga|T047|EQV|GHR (2014)|130418|abdef
SY = 2-Hydroxyglutaric Aciduria|T047|EQV|GHR (2014)|130418|abdef
SY = Combined D-2- and L-2-hydroxyglutaric aciduria|T047|EQV|ORD (2010)|090615|abdef
SY = D-2-hydroxyglutaric aciduria|T047|EQV|OMIM (2013)|ORD (2010)|090615|abdeef
SY = L-2-Hydroxyglutaric Acidemia|T047|EQV|OMIM (2013)|111115|abdef
SY = L-2-hydroxyglutaric aciduria|T047|EQV|OMIM (2013)|ORD (2010)|090615|abdeef
HM = Brain Diseases, Metabolic, Inborn
NM_TH = ORD (2010)
ST = T047
FR = 38
NO = Hereditary neurometabolic disorders characterized by DEVELOPMENTAL DELAY; EPILEPSY; HYPOTONIA, and dysmorphic features. Severe cases of D2HGA are homogeneous and are characterized by early infantile-onset epileptic encephalopathy and, CARDIOMYOPATHY. The mild phenotype has a more variable clinical presentation. In L2HGA, patients may also present with ATAXIA; MEGALENCEPHALY, and speech difficulties and the condition deteriorates over time. Mutations in the D2HGDH gene have been identified for D2HGA (OMIM: 600721) and the L2HGDH gene for L2HGA (OMIM: 236792).
DA = 20100625
MR = 20150808
UI = C535306
"""


def load_mesh_supp():
    semantic_types, disorders = load_semantic_types()

    attributes = {'HM': "mapped_to",
                  'MR': "last_updated",
                  'NM': "tree",
                  'NO': "note",
                  'RECTYPE': "record_type",
                  'ST': "semantic_type",
                  'SY': "synonym",
                  'UI': "_id"}

    # read in the mesh data
    with open(supp_path) as f:
        mesh_supp = [x.strip() for x in f.readlines()]

    # which attributes can have multiple values?
    gb = filterfalse(lambda x: x[0], groupby(mesh_supp, lambda x: x == "*NEWRECORD"))
    ds = []
    for gb_record in gb:
        record = list(gb_record[1])
        d = dict(Counter([line.split("=", 1)[0].strip() for line in record if "=" in line]))
        ds.append(d)
    df = pd.DataFrame(ds).fillna(0)
    list_attribs = set(df.columns[df.max() > 1])

    # split into records
    gb = filterfalse(lambda x: x[0], groupby(mesh_supp, lambda x: x == "*NEWRECORD"))

    mesh_supp_terms = []
    for gb_record in gb:
        record = list(gb_record[1])
        d = defaultdict(list)
        for line in record:
            if "=" not in line:
                continue
            key = line.split("=", 1)[0].strip()
            value = line.split("=", 1)[1].strip()
            if key in list_attribs and key in attributes:
                d[attributes[key]].append(value)
            elif key in attributes and key not in {"SY"}:
                d[attributes[key]] = value
            elif key == "SY":
                d['synonyms'].append(value.split("|", 1)[0])

        if not (set(d['semantic_type']) & disorders):
            continue
        d['semantic_type_id'] = d['semantic_type']
        d['semantic_type'] = [semantic_types[c] for c in d['semantic_type']]
        d['_id'] = "mesh:" + d['_id']
        mesh_supp_terms.append(dict(d))

    return mesh_supp_terms


def parse(mongo_collection=None, drop=True):
    if mongo_collection:
        db = mongo_collection
    else:
        client = MongoClient()
        db = client.mydisease.mesh
    if drop:
        db.drop()
    mesh_terms = load_mesh_desc()
    mesh_supp_terms = load_mesh_supp()
    db.insert_many(mesh_terms)
    db.insert_many(mesh_supp_terms)
