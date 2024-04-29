def get_customized_mapping(cls):
    mapping = {
        "disease_ontology": {
            "properties": {
                "ancestors": {
                    "type": "keyword",
                    "normalizer": "keyword_lowercase_normalizer"
                },
                "children": {
                    "type": "keyword",
                    "normalizer": "keyword_lowercase_normalizer"
                },
                "def": {
                    "type": "text"
                },
                "descendants": {
                    "type": "keyword",
                    "normalizer": "keyword_lowercase_normalizer"
                },
                "doid": {
                    "type": "keyword",
                    "normalizer": "keyword_lowercase_normalizer"
                },
                "name": {
                    "type": "text",
                    "copy_to": [
                        "all"
                    ]
                },
                "parents": {
                    "type": "keyword",
                    "normalizer": "keyword_lowercase_normalizer"
                },
                "synonyms": {
                    "properties": {
                        "exact": {
                            "type": "text",
                            "copy_to": [
                                "all"
                            ]
                        },
                        "related": {
                            "type": "text"
                        }
                    }
                },
                "xrefs": {
                    "properties": {
                        "efo": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "gard": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "icd10": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "icd9": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "icdo": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "kegg": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "meddra": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "mesh": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "ncit": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "omim": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "ordo": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "snomedct_us_2018_03_01": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "snomedct_us_2019_09_01": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "snomedct_us_2020_03_01": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "snomedct_us_2020_09_01": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "umls_cui": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        }
                    }
                }
            }
        }
    }
    return mapping
