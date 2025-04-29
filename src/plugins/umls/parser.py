import glob
import os
import re
import urllib
import zipfile
from typing import Union

import bs4
import requests
from biothings.utils.common import open_anyfile

from .umls_secret import UMLS_API_KEY

try:
    from biothings import config
    logger = config.logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


SAB_MAPPING = {
    'NCI': 'nci',
    'MSH': 'mesh',
    'SNOMEDCT_US': 'snomed',
    'ICD10CM': 'icd10cm',
    'ICD10': 'icd10',
    'ICD10AM': 'icd10am',
    'ICD9CM': 'icd9cm'
}
DISEASE_SEMANTIC_TYPES = {
    "Disease or Syndrome",
    "Congenital Abnormality",
    "Acquired Abnormality",
    "Injury or Poisoning",
    "Pathologic Function",
    "Mental or Behavioral Dysfunction",
    "Cell or Molecular Dysfunction",
    "Anatomical Abnormality",
    "Neoplastic Process",
}
PHENOTYPE_SEMANTIC_TYPES = {
    "Finding",
    "Laboratory or Test Result",
    "Sign or Symptom",
    "Organism Attribute",
}
WANTED_LAT = 'ENG'
TS_MAPPING = {
    'P': 'preferred',
    'S': 'non-preferred'
}
API_ENDPOINT = 'http://mydisease.info/v1/query'
WANTED_SEMANTIC_TYPES = DISEASE_SEMANTIC_TYPES | PHENOTYPE_SEMANTIC_TYPES


class ParserException(Exception):
    pass


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
        data = {'q': ', '.join(
            cui_page), 'scopes': 'mondo.xrefs.umls,disgenet.xrefs.umls'}
        response = s.post(API_ENDPOINT, data=data)
        for result in response.json():
            cui = result['query']
            # either build a list of primary IDs or use UMLS:id
            if '_id' in result:
                primary_id_mapping.setdefault(cui, []).append(result['_id'])
            elif result.get('notfound', False):
                primary_id_mapping[cui] = [f'UMLS:{cui}']
    return primary_id_mapping


def get_download_url():
    res = requests.get(
        "https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html")
    # Raise error if status is not 200
    res.raise_for_status()
    html = bs4.BeautifulSoup(res.text, 'lxml')
    # Get the table of metathesaurus release files
    table = html.find(
        "table", attrs={"class": "usa-table border-base-lighter margin-bottom-4"})
    rows = table.find_all('tr')
    # The header of the first column should be 'Release'
    assert rows[0].find_all('th')[0].text.strip(
    ) == 'Release', "Could not parse url from html table."
    try:
        # Get the url from the link
        url = rows[1].find_all('td')[0].a["href"]
        # Create the url using the api aky
        url = f'https://uts-ws.nlm.nih.gov/download?url={url}&apiKey={UMLS_API_KEY}'
        return url
    except Exception as e:
        raise ParserException(
            f"Can't find or parse url from table field {url}: {e}")


def load_data(data_folder):
    try:
        metathesaurus_file = glob.glob(os.path.join(
            data_folder, '*metathesaurus-release.zip'))[0]
    except IndexError:
        url = get_download_url()
        # Use re.sub to replace all characters after "apiKey=" with asterisks
        pii_url = re.sub(r"(apiKey=).*", r"\1" + "*" *
                         len(re.search(r"(apiKey=)(.*)", url).group(2)), url)
        logger.info("""Could not find metathesaurus archive in {}.
                     Downloading UMLS Metathesaurus file automatically:
                     {}
                     """.format(data_folder, pii_url))
        # Download UMLS file to data folder
        urllib.request.urlretrieve(url, os.path.join(
            data_folder, 'metathesaurus-release.zip'))
        # Get the downloaded file path
        metathesaurus_file = glob.glob(os.path.join(
            data_folder, '*metathesaurus-release.zip'))[0]
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
    umls_xrefs = parse_mrconso(
        metathesaurus_file, mrconso_path, wanted=cui_wanted)
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
            logger.info(
                f"Primary ID {primary_id} is mapped to multiple CUIs: {primary_id_to_cui[primary_id]}")

    # Set primary id for documents. Create duplicate documents for the one-to-many case.
    for cui in umls_xrefs:
        for primary_id in primary_id_map[cui]:
            umls_xref = umls_xrefs[cui]
            umls_xref['_id'] = primary_id
            yield umls_xref
