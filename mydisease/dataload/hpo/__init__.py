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