import hashlib
import json
import xml.etree.ElementTree as et
import gzip
import os
import pandas as pd
from django.core.files.storage import default_storage
from unidecode import unidecode
from .models import MeSH_Term

# todo: Use s3
DATA_DIR = os.path.dirname(os.path.realpath(__file__))


def md5_of_file(fname):
    hash_md5 = hashlib.md5()
    with default_storage.open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def populate_mesh():
    """
    Initially populate mesh term. Only works starting with empty table

    """
    # Read MeSH descriptor and supplementary terms
    desc_df = pd.read_table(os.path.join(DATA_DIR, 'data/descriptor-terms.tsv'))
    supp_df = pd.read_table(os.path.join(DATA_DIR, 'data/supplemental-terms.tsv'))
    desc_df.TermName = desc_df.TermName.str.lower()
    supp_df.TermName = supp_df.TermName.str.lower()
    # Get the preferred name for each term
    preferred_name = dict()
    for term, df in desc_df.groupby("DescriptorUI"):
        preferred_name[term] = list(df[(df.PreferredConceptYN == "Y") & (df.ConceptPreferredTermYN == "Y") & (
            df.RecordPreferredTermYN == "Y")].TermName)[0]
    for term, df in supp_df.groupby("SupplementalRecordUI"):
        preferred_name[term] = list(df[(df.PreferredConceptYN == "Y") & (df.ConceptPreferredTermYN == "Y") & (
            df.RecordPreferredTermYN == "Y")].TermName)[0]
    # Fix unicode nonsense
    upreferred_name = {k: unidecode(v.decode('utf-8')) for k, v in preferred_name.items()}

    # Check unicode munging
    # {preferred_name[k]:upreferred_name[k] for k,v in preferred_name.items() if preferred_name[k] != upreferred_name[k]}

    # Batch insert
    mesh_obj = [MeSH_Term(id=x[0], name=x[1]) for x in upreferred_name.items()]
    MeSH_Term.objects.bulk_create(mesh_obj, batch_size=10000)


def run_mesh():
    """
    Only updated once a year.
    ftp://nlmpubs.nlm.nih.gov/online/mesh/2016/desc2016.xml
    ftp://nlmpubs.nlm.nih.gov/online/mesh/2016/supp2016.xml
    """
    # TODO check if file exists. download it if not. Check year, change path to match current year?
    parse_mesh_xml(os.path.join(DATA_DIR, 'data/desc2016.xml'))
    parse_mesh_xml(os.path.join(DATA_DIR, 'data/supp2016.xml'))
    parse_mesh_parents(os.path.join(DATA_DIR, 'data/desc2016.xml'))
    populate_mesh()


def parse_mesh_parents(xml_path):
    """
    Get the heirarchy of mesh terms.
    Not doing anything with this yet...

    :param xml_path: path to "desc2016.xml" file
    :return: None
    """
    terms = list()
    f = open(xml_path)
    context = iter(et.iterparse(f, events=("start", "end")))
    event, root = next(context)
    for event, elem in context:
        if event == "end" and elem.tag == "DescriptorRecord":
            term = dict()
            term['mesh_id'] = elem.findtext('DescriptorUI')
            term['mesh_name'] = elem.findtext('DescriptorName/String')
            term['tree_numbers'] = [x.text for x in elem.findall('TreeNumberList/TreeNumber')]
            terms.append(term)
        root.clear()

    # shamelessy stolen from https://github.com/dhimmel/mesh/blob/gh-pages/descriptors.ipynb
    # Determine ontology parents
    tree_number_to_id = {tn: term['mesh_id'] for term in terms for tn in term['tree_numbers']}
    for term in terms:
        parents = set()
        for tree_number in term['tree_numbers']:
            try:
                parent_tn, self_tn = tree_number.rsplit('.', 1)
                parents.add(tree_number_to_id[parent_tn])
            except ValueError:
                pass
        term['parents'] = list(parents)

    with open(os.path.join(DATA_DIR, 'data', 'mesh.json'), 'w') as f:
        json.dump(terms, f, indent=2)


def parse_mesh_xml(xml_path):
    # based on: https://github.com/dhimmel/mesh/blob/gh-pages/descriptors.ipynb
    if "desc" in os.path.basename(xml_path):
        record_name = "DescriptorRecord"
        recordUI = "DescriptorUI"
        out_tsv = "descriptor-terms.tsv"
    elif "supp" in os.path.basename(xml_path):
        record_name = "SupplementalRecord"
        recordUI = "SupplementalRecordUI"
        out_tsv = "supplemental-terms.tsv"
    else:
        raise ValueError("Unknown mesh xml type")

    f = open(xml_path)
    # for parsing an xml iteratively (without using 6gb of ram)
    context = iter(et.iterparse(f, events=("start", "end")))
    event, root = next(context)
    term_dicts = list()
    for event, elem in context:
        if event == "end" and record_name == elem.tag:
            for concept in elem.findall("ConceptList/Concept"):
                for term in concept.findall('TermList/Term'):
                    term_dict = {
                        recordUI: elem.findtext(recordUI),
                        'ConceptUI': concept.findtext('ConceptUI'),
                        'TermUI': term.findtext('TermUI'),
                        'TermName': term.findtext('String')
                    }
                    term_dict.update(concept.attrib)
                    term_dict.update(term.attrib)
                    term_dicts.append(term_dict)
        root.clear()

    columns = [recordUI, 'ConceptUI', 'PreferredConceptYN', 'TermUI', 'TermName', 'ConceptPreferredTermYN',
               'RecordPreferredTermYN', ]
    term_df = pd.DataFrame(term_dicts)[columns]
    term_df.to_csv(os.path.join(DATA_DIR, 'data', out_tsv), encoding='utf-8')


"""
Don't know if we need this as a lookup

# go from a supplemental concept to a descriptor
df = supp_df[supp_df.SupplementalRecordUI=='C031234']
list(df[(df.PreferredConceptYN == "Y") & (df.ConceptPreferredTermYN == "Y") & (df.RecordPreferredTermYN == "Y")].TermName)[0]

# Create a dictionary of MeSH term names to unique identifiers
mesh_name_to_id = dict(zip(desc_df.TermName.str.lower(), desc_df.DescriptorUI))
mesh_name_to_id.update(dict(zip(supp_df.TermName.str.lower(), supp_df.SupplementalRecordUI)))

"""
