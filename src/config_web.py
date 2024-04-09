import re

# *****************************************************************************
# Elasticsearch variables
# *****************************************************************************
ES_HOST = 'http://localhost:9200'
ES_ARGS = dict(request_timeout=60)
ES_INDICES = dict(disease='mydisease_current')

# *****************************************************************************
# Web Application
# *****************************************************************************
API_VERSION = 'v1'

# *****************************************************************************
# Features
# *****************************************************************************

STATUS_CHECK = {
    'id': 'MONDO:0021004',
    'index': 'mydisease_current'
}

ANNOTATION_ID_REGEX_LIST = [
    # Matches MONDO IDs (MONDO:xxxx) regardless of case
    (re.compile(r'MONDO\:[0-9]+', re.I), ('mondo.mondo', '_id',
     'disgenet.xrefs.mondo', 'disease_ontology.xrefs.mondo', 'mondo.xrefs.mondo')),
    # Matches MESH IDs (e.g., "MESH:XXXX") or no-prefix IDs starting with "D" or "C" followed by digits (e.g., "D000086382", "C5203670").
    (re.compile(r'([DC][0-9]+|MESH\:[A-Z0-9]+)', re.I), ('mondo.xrefs.mesh', '_id', 'disease_ontology.xrefs.mesh',
     'ctd.mesh', 'disgenet.xrefs.mesh', 'umls.mesh', 'disease_ontology.xrefs.mesh', 'disease_ontology.xrefs.ncit', 'mondo.xrefs.ncit')),
    # Matches Disease Ontology IDs (DOID:xxxx) regardless of case
    (re.compile(r'DOID\:[0-9]+', re.I), ('disease_ontology.doid',
     'disgenet.xrefs.doid', 'mondo.xrefs.doid', '_id')),
    # Matches OMIM IDs (OMIM:xxxx) regardless of case or no prefix IDs with only digits
    (re.compile(r'(OMIM\:)?[0-9]+', re.I), ('_id', 'ctd.omim',
     'disease_ontology.xrefs.omim', 'disgenet.xrefs.omim', 'hpo.omim', 'mondo.xrefs.omim')),
    # Matches HP IDs (HP:xxxx) regardless of case
    (re.compile(r'HP\:[0-9]+', re.I),
     ('disgenet.xrefs.hp', 'mondo.xrefs.hp')),
    # Matches ORPHANET IDs (ORPHANET:xxxx) regardless of case
    (re.compile(r'ORPHANET\:[0-9]+', re.I),
     ('_id', 'mondo.xrefs.orphanet', 'hpo.orphanet')),
    # Matches UMLS IDs (UMLS:xxxx) regardless of case
    (re.compile(r'UMLS\:[A-Z0-9]+', re.I), ('_id',
     'mondo.xrefs.umls', 'umls.umls', 'disgenet.xrefs.umls')),
    # Matches DECIPHER IDs (DECIPHER:xxxx) regardless of case
    (re.compile(r'DECIPHER\:[0-9]+', re.I), ('_id', 'hpo.decipher')),
    # Matches KEGG.DISEASE IDs (H00031) regardless of case NOTE KEGG.DISEASE IDs are not in the data
    (re.compile(r'^H\d+$', re.I), #double check parser
     ('disease_ontology.xrefs.kegg', 'mondo.xrefs.kegg')),
    # Matches ICD9 IDs (255.4) regardless of case
    (re.compile(r'^\d{3}(\.\d{1,2})?$', re.I),
     ('disease_ontology.xrefs.icd9', 'disgenet.xrefs.icd9', 'mondo.xrefs.icd9')),
    # Matches ICD10 IDs (U07.1) regardless of case
    (re.compile(r'^[A-Z][0-9][0-9A-Z]?(?:\.[0-9A-Z]{1,5})?$', re.I),
     ('disease_ontology.xrefs.icd10', 'disgenet.xrefs.icd10', 'mondo.xrefs.icd10')),
    # Matches ICD11 IDs (CA01.001) regardless of case NOTE ICD11 IDs are not in the data
    (re.compile(
        r'^[A-NP-Z][0-9]([0-9A-Z]{0,5})?$', re.I), 'mondo.xrefs.icd11'),
]
