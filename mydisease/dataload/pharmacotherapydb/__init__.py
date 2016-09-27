import os

from mydisease import DATA_DIR

__METADATA__ = {
    "src_name": 'PharmacotherapyDB',
    "src_url": 'https://thinklab.com/discussion/announcing-pharmacotherapydb-the-open-catalog-of-drug-therapies-for-disease',
    "field": "pharmacotherapydb",
    "version": "1",
    "license": "CC0 1.0",
    "license_url": "https://github.com/dhimmel/indications"
}

# downloaded from: https://github.com/dhimmel/indications
url = "https://raw.githubusercontent.com/dhimmel/indications/11d535ba0884ee56c3cd5756fdfb4985f313bd80/catalog/indications.tsv"
file_path = os.path.join(DATA_DIR, "indications.tsv")


def get_mapping():
    mapping = {
        "pharmacotherapydb": {
            "properties": {
                "indications": {
                    "properties": {
                        "category": {
                            "type": "string",
                        },
                        "drug": {
                            "type": "string"
                        },
                        "drugbank_id": {
                            "type": "string",
                        },
                        "n_curators": {
                            "type": "integer",
                            "index": "no"
                        },
                        "n_resources": {
                            "type": "integer",
                            "index": "no"
                        }
                    }
                }
            }
        }
    }
    return mapping


jsonld = {
    "pharmacotherapydb": {
        "@context": {"indications": ""}
    },
    "pharmacotherapydb/indications": {
        "@context": {
            "drugbank_id": "http://identifiers.org/drugbank/",
        }
    }
}