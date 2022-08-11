import glob
import logging
import os
import zipfile
from typing import Union

import requests
from biothings.utils.common import open_anyfile

SAB_MAPPING = {
    'NCI': 'nci',
    'MSH': 'mesh',
    'SNOMEDCT_US': 'snomed',
    'ICD10CM': 'icd10cm',
    'ICD10': 'icd10',
    'ICD10AM': 'icd10am',
    'ICD9CM': 'icd9cm'
}
WANTED_SEMANTIC_TYPES = [
    'Disease or Syndrome',
    'Mental or Behavioral Dysfunction',
    'Neoplastic Process'
]
WANTED_LAT = 'ENG'
TS_MAPPING = {
    'P': 'preferred',
    'S': 'non-preferred'
}
API_ENDPOINT = 'http://mydisease.info/v1/query'


def unlist_and_deduplicate(input_list):
    s = set(input_list)
    assert len(s) > 0
    if len(s) == 1:
        return s.pop()
    return list(s)


def paginate(input_list: list, p: int):
    for idx in range(0, len(input_list), p):
        yield input_list[idx:idx + p]


def parse_mrsty(archive_path, data_path: Union[str, bytes]) -> set:
    cuis = set()  # make sure they are unique
    with open_anyfile((archive_path, data_path), 'r') as f:
        for line in f:
            cui, tui, stn, sty = line.rstrip('\n').split('|')[:4]
            # extract whatever we are interested in
            if sty in WANTED_SEMANTIC_TYPES:
                cuis.add(cui)
    return cuis


def parse_mrconso(archive_path, data_path: Union[str, bytes], wanted: set) -> dict:
    umls_xrefs = {}
    with open_anyfile((archive_path, data_path), 'r') as f:
        for line in f:
            line = line.rstrip('\n').split('|')
            cui, lat, ts = line[:3]
            # ignore the line if language not wanted or not a disease
            if not lat == WANTED_LAT or cui not in wanted:
                continue
            sab, _, code = line[11:14]
            if sab not in SAB_MAPPING:
                continue  # we are not interested in it
            umls_xrefs.setdefault(cui, {}).setdefault("umls", {}).setdefault(SAB_MAPPING[sab], {}).setdefault(
                TS_MAPPING[ts], []).append(code)
    # I wanted to use map() but doing it nested is harder than this
    for cui in umls_xrefs:
        for sab in umls_xrefs[cui]["umls"]:
            for preferred in umls_xrefs[cui]["umls"][sab]:
                umls_xrefs[cui]["umls"][sab][preferred] = unlist_and_deduplicate(
                    umls_xrefs[cui]["umls"][sab][preferred])
        umls_xrefs[cui]['umls']['umls'] = cui
    return umls_xrefs


def get_primary_ids(cuis: list):
    primary_id_mapping = {}
    s = requests.Session()
    for cui_page in paginate(list(cuis), 1000):
        data = {'q': ', '.join(cui_page), 'scopes': 'mondo.xrefs.umls,disgenet.xrefs.umls'}
        response = s.post(API_ENDPOINT, data=data)
        for result in response.json():
            cui = result['query']
            # either build a list of primary IDs or use UMLS:id
            if '_id' in result:
                primary_id_mapping.setdefault(cui, []).append(result['_id'])
            elif result.get('notfound', False):
                primary_id_mapping[cui] = [f'UMLS:{cui}']
    return primary_id_mapping


def load_data(data_folder):
    try:
        metathesaurus_file = glob.glob(os.path.join(data_folder, '*metathesaurus.zip'))[0]
    except IndexError:
        raise FileNotFoundError(
            """Could not find metathesaurus archive in {}.
            Please download UMLS Metathesaurus file manually from:
            https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html
            """.format(data_folder))
    file_list = zipfile.ZipFile(metathesaurus_file, mode='r').namelist()
    try:
        mrsty_path = [f for f in file_list if f.endswith('MRSTY.RRF')][0]
    except IndexError:
        raise FileNotFoundError("Could not find MRSTY.RRF in archive.")
    try:
        mrconso_path = [f for f in file_list if f.endswith('MRCONSO.RRF')][0]
    except IndexError:
        raise FileNotFoundError("Could not find MRCONSO.RRF in archive.")
    # Parse files
    cui_wanted = parse_mrsty(metathesaurus_file, mrsty_path)
    umls_xrefs = parse_mrconso(metathesaurus_file, mrconso_path, wanted=cui_wanted)
    # obtain primary id for CUIs that actually has data
    # TODO: I don't like how every time it has to call the APIs to get the primary IDs
    primary_id_map = get_primary_ids(list(umls_xrefs.keys()))

    # Reverse the mapping to get the primary_id to CUI mapping and check for duplicates
    # CUI/UMLS to _id relationship is many-to-many, and we use Merger storage to combine fields.
    # We can use this list to check that the merge happens correctly.
    primary_id_to_cui = {}
    for cui in umls_xrefs:
        for primary_id in primary_id_map[cui]:
            primary_id_to_cui.setdefault(primary_id, []).append(cui)
    for primary_id in primary_id_to_cui:
        if len(primary_id_to_cui[primary_id]) > 1:
            logging.info(f"Primary ID {primary_id} is mapped to multiple CUIs: {primary_id_to_cui[primary_id]}")

    # Set primary id for documents. Create duplicate documents for the one-to-many case.
    for cui in umls_xrefs:
        for primary_id in primary_id_map[cui]:
            umls_xref = umls_xrefs[cui]
            umls_xref['_id'] = primary_id
            yield umls_xref
