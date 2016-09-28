import os

from mydisease import DATA_DIR

__METADATA__ = {
    "src_name": 'Orphanet',
    "src_url": 'http://www.orpha.net/consor/cgi-bin/index.php',
    "release": "V2.2",
    "field": "orphanet",
    "license": "CC-BY-ND 3.0",
    "license_url": "http://www.orphadata.org/cgi-bin/inc/legal.inc.php"
}

# downloaded from: http://www.orphadata.org/cgi-bin/index.php

# http://www.orphadata.org/cgi-bin/inc/ordo_orphanet.inc.php
ordo_url = "http://data.bioontology.org/ontologies/ORDO/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv"
ordo_path = os.path.join(DATA_DIR, "ORDO.csv.gz")

# http://www.orphadata.org/cgi-bin/inc/product1.inc.php
# Rare diseases and cross-referencing
xref_url = "http://www.orphadata.org/data/xml/en_product1.xml"
xref_path = os.path.join(DATA_DIR, os.path.split(xref_url)[1])

# http://www.orphadata.org/cgi-bin/inc/product2.inc.php
# Rare diseases epidemiological data
# Point prevalence, prevalence at birth, lifetime prevalence, annual incidence, number of cases an/or families
prev_url = "http://www.orphadata.org/data/xml/en_product2_prev.xml"
prev_path = os.path.join(DATA_DIR, os.path.split(prev_url)[1])
# Type of inheritance, average age of onset and average age of death
ages_url = "http://www.orphadata.org/data/xml/en_product2_ages.xml"
ages_path = os.path.join(DATA_DIR, os.path.split(ages_url)[1])

# http://www.orphadata.org/cgi-bin/inc/product4.inc.php
# Phenotypes associated with rare disorders
hpo_url = "http://www.orphadata.org/data/xml/en_product4_HPO.xml"
hpo_path = os.path.join(DATA_DIR, os.path.split(hpo_url)[1])

# http://www.orphadata.org/cgi-bin/inc/product6.inc.php
# Rare diseases with their associated genes
gene_url = "http://www.orphadata.org/data/xml/en_product6.xml"
gene_path = os.path.join(DATA_DIR, os.path.split(gene_url)[1])


def get_mapping():
    mapping = {
        "orphanet": {
            "properties": {
                "mapping": {
                    "properties": {
                        "NTBT": {
                            "type": "string"
                        },
                        "E": {
                            "type": "string"
                        },
                        "BTNT": {
                            "type": "string"
                        },
                        "ND": {
                            "type": "string"
                        }
                    }
                },
                "ave_age_of_onset": {
                    "type": "string"
                },
                "preferred_label": {
                    "type": "string"
                },
                "reason_for_obsolescence": {
                    "type": "string"
                },
                "part_of": {
                    "type": "string"
                },
                "disease_gene_associations": {
                    "properties": {
                        "gene_symbol": {
                            "type": "string"
                        },
                        "loci": {
                            "type": "string"
                        },
                        "dga_type": {
                            "type": "string"
                        },
                        "gene_name": {
                            "type": "string"
                        },
                        "dga_status": {
                            "type": "string"
                        },
                        "gene_type": {
                            "type": "string"
                        }
                    }
                },
                "ave_age_of_death": {
                    "type": "string"
                },
                "phenotypes": {
                    "properties": {
                        "phenotype_id": {
                            "type": "string"
                        },
                        "phenotype_name": {
                            "type": "string"
                        },
                        "frequency": {
                            "type": "string"
                        }
                    }
                },
                "definition_citation": {
                    "type": "string"
                },
                "definitions": {
                    "type": "string"
                },
                "type_of_inheritance": {
                    "type": "string"
                },
                "xref": {
                    "properties": {
                        "mesh": {
                            "type": "string"
                        },
                        "icd10cm": {
                            "type": "string"
                        },
                        "meddra": {
                            "type": "string"
                        },
                        "umls_cui": {
                            "type": "string"
                        },
                        "omim": {
                            "type": "string"
                        }
                    }
                },
                "prevalence": {
                    "properties": {
                        "prevalence_class": {
                            "type": "string"
                        },
                        "prevalence_type": {
                            "type": "string"
                        },
                        "mean_value": {
                            "type": "long"
                        },
                        "source": {
                            "type": "string"
                        },
                        "prevalence_validation_status": {
                            "type": "string"
                        },
                        "prevalence_qualification": {
                            "type": "string"
                        },
                        "prevalence_geographic": {
                            "type": "string"
                        }
                    }
                },
                "parents": {
                    "type": "string"
                },
                "tree_view": {
                    "type": "string"
                },
                "definition": {
                    "type": "string"
                },
                "alternative_term": {
                    "type": "string"
                },
                "synonyms": {
                    "type": "string"
                },
                "_id": {
                    "type": "string"
                }
            }
        }
    }
    return mapping
