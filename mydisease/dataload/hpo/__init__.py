import os

from mydisease import DATA_DIR

__METADATA__ = {
    "src_name": 'Human Phenotype Ontology',
    "src_url": 'http://human-phenotype-ontology.github.io/',
    "release": "September 2016",
    "field": "hpo",
    "license": "custom",
    "license_url": "http://human-phenotype-ontology.github.io/license.html"
}

# downloaded from: http://human-phenotype-ontology.github.io/downloads.html
url = "http://purl.obolibrary.org/obo/hp.obo"
file_path = os.path.join(DATA_DIR, "hp.obo")


def get_mapping():
    mapping = {
        "hpo": {
            "properties": {
                "comment": {
                    "type": "string"
                },
                "creation_date": {
                    "type": "string"
                },
                "subset": {
                    "type": "string"
                },
                "created_by": {
                    "type": "string"
                },
                "is_a": {
                    "type": "string"
                },
                "_id": {
                    "type": "string"
                },
                "is_anonymous": {
                    "type": "string"
                },
                "synonym": {
                    "type": "string"
                },
                "xref": {
                    "properties": {
                        "eurenomics": {
                            "type": "string"
                        },
                        "mesh": {
                            "type": "string"
                        },
                        "pmid": {
                            "type": "string"
                        },
                        "ki": {
                            "type": "string"
                        },
                        "ncit": {
                            "type": "string"
                        },
                        "nihr": {
                            "type": "string"
                        },
                        "hp": {
                            "type": "string"
                        },
                        "eom": {
                            "type": "string"
                        },
                        "snomedct": {
                            "type": "string"
                        },
                        "icd10cm": {
                            "type": "string"
                        },
                        "neuromics": {
                            "type": "string"
                        },
                        "icm": {
                            "type": "string"
                        },
                        "orcid": {
                            "type": "string"
                        },
                        "goc": {
                            "type": "string"
                        },
                        "umls_cui": {
                            "type": "string"
                        },
                        "mp": {
                            "type": "string"
                        },
                        "uk": {
                            "type": "string"
                        },
                        "meddra": {
                            "type": "string"
                        },
                        "utoronto": {
                            "type": "string"
                        },
                        "epcc": {
                            "type": "string"
                        }
                    }
                },
                "alt_id": {
                    "type": "string"
                },
                "name": {
                    "type": "string"
                },
                "def": {
                    "type": "string"
                }
            }
        }
    }
    return mapping


jsonld = {"hpo": {
    "@context": {
        "is_a": "https://www.w3.org/2000/01/rdf-schema#subClassOf",
        "name": "http://www.w3.org/2000/01/rdf-schema#label",
        "synonym": "http://www.geneontology.org/formats/oboInOwl#hasExactSynonym",
        "xref": "http://www.geneontology.org/formats/oboInOwl#hasDbXref"
    }
},
    "hpo/xref": {
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
