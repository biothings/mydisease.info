
from curses import meta
import os
from tkinter import W
from typing import Union

from biothings.utils.common import open_anyfile
import requests


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
    with open_anyfile((archive_path, data_path), 'rt') as f:
        for line in f:
            cui, tui, stn, sty = line.rstrip('\n').split('|')[:4]
            # extract whatever we are interested in
            if sty in WANTED_SEMANTIC_TYPES:
                cuis.add(cui)
    return cuis


def parse_mrconso(archive_path, data_path: Union[str, bytes], wanted: set) -> dict:
    umls_xrefs = {}
    with open_anyfile((archive_path, data_path), 'rt') as f:
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
        # FIXME: using only MONDO xrefs here, until disgenet issue is fixed
        data = {'q': ', '.join(cui_page), 'scopes': 'mondo.xrefs.umls'}
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
    metathesaurus_file = os.path.join(data_folder, glob.glob('*metathesaurus.zip')[0])
    if not metathesaurus_file():
        raise FileNotFoundError(
            """Could not find metathesaurus archive in {}.
            Please download UMLS Metathesaurus file manually and extract to folder.
            """.format(data_folder))
    file_list = ZipFile(metathesaurus_file).namelist()
    mrsty_path = [f for f in file_list if f.endswith('MRSTY.RRF')][0]
    assert len(mrsat_path) == 1, "Could not find MRSAT.RRF in archive."
    mrconso_path = [f for f in file_list if f.endswith('MRCONSO.RRF')][0]
    assert len(mrconso_path) == 1, "Could not find MRCONSO.RRF in archive."
    cui_wanted = parse_mrsty(metathesaurus_file, mrsty_path)
    umls_xrefs = parse_mrconso(metathesaurus_file, mrconso_path, wanted=cui_wanted)
    # obtain primary id for CUIs that actually has data
    # TODO: I don't like how every time it has to call the APIs to get the primary IDs
    primary_id_map = get_primary_ids(list(umls_xrefs.keys()))
    # TODO: Check output uniqueness per _id
    #  CUI/UMLS - primary_id is at least one-to-many, but could be many-to-many
    #  I still set on_duplicates in the manifest.json to be "ignore" so it will run
    #  as we may need a slightly different document schema for many-to-many scenarios
    for cui in umls_xrefs:
        for primary_id in primary_id_map[cui]:
            umls_xref = umls_xrefs[cui]
            umls_xref['_id'] = primary_id
            yield umls_xref
#/