import os

from mydisease import DATA_DIR

__METADATA__ = {
    "src_name": 'Disease Ontoloy',
    "src_url": 'http://disease-ontology.org/',
    "field": "disease_ontoloy",
    "version": "2016-09-26",
    "license": "CC-BY-3.0",
    "license_url": "https://raw.githubusercontent.com/DiseaseOntology/HumanDiseaseOntology/master/DO_LICENSE.txt"
}

# downloaded from: http://ctdbase.org/downloads/
url = "http://purl.obolibrary.org/obo/doid.obo"
file_path = os.path.join(DATA_DIR, "doid.obo")


def get_mapping():
    mapping = {
        'disease_ontoloy': {
            'properties': {'_id': {'type': 'string'},
                           'alt_id': {'type': 'string'},
                           'comment': {'type': 'string'},
                           'created_by': {'type': 'string'},
                           'creation_date': {'type': 'string'},
                           'def': {'type': 'string'},
                           'is_a': {'type': 'string'},
                           'name': {'type': 'string'},
                           'subset': {'type': 'string'},
                           'synonym': {'type': 'string'},
                           'xref': {
                               'properties': {
                                   'csp': {'type': 'string'},
                                   'ctv3': {'type': 'string'},
                                   'efo': {'type': 'string'},
                                   'efopat_id': {'type': 'string'},
                                   'hp': {'type': 'string'},
                                   'https': {'type': 'string'},
                                   'icd10cm': {'type': 'string'},
                                   'icd9cm': {'type': 'string'},
                                   'kegg': {'type': 'string'},
                                   'ls': {'type': 'string'},
                                   'meddra': {'type': 'string'},
                                   'mesh': {'type': 'string'},
                                   'nci': {'type': 'string'},
                                   'nci2009_04d': {'type': 'string'},
                                   'omim': {'type': 'string'},
                                   'omm': {'type': 'string'},
                                   'orphanet': {'type': 'string'},
                                   'pmid': {'type': 'string'},
                                   'sn': {'type': 'string'},
                                   'snomedct': {'type': 'string'},
                                   'snomedct_us_2016_03_01': {'type': 'string'},
                                   'stedman': {'type': 'string'},
                                   'umls_cui': {'type': 'string'},
                                   'url': {'type': 'string'}
                               }
                           }
                           }
        }
    }
    return mapping


jsonld = {"doid": {
    "@context": {
        "is_a": "https://www.w3.org/2000/01/rdf-schema#subClassOf",
        "name": "http://www.w3.org/2000/01/rdf-schema#label",
        "synonym": "http://www.geneontology.org/formats/oboInOwl#hasExactSynonym",
        "xref": "http://www.geneontology.org/formats/oboInOwl#hasDbXref"
    }
},
    "doid/xref": {
        "@context": {
            "mesh": "http://identifers.org/mesh/",
            "orphanet": "http://identifiers.org/orphanet.ordo/",
            "umls_cui": "http://identifiers.org/umls/",
            "snomedct_us_2016_03_01": "http://identifiers.org/snomedct/",
            "nci": "",
            "icd10cm": "http://identifiers.org/icd/",
            "icd9cm": "",
            "omim": "http://identifiers.org/omim/",
            "efo": "http://identifiers.org/efo/",
            "kegg": "http://identifiers.org/kegg.disease/",
            "url": ""
        }
    }
}
