def get_customized_mapping(cls):
    mapping = {
        "disgenet": {
            "properties": {
                "genes_related_to_disease": {
                    "properties": {
                        "DPI": {
                            "type": "float"
                        },
                        "DSI": {
                            "type": "float"
                        },
                        "EI": {
                            "type": "float"
                        },
                        "YearFinal": {
                            "type": "integer"
                        },
                        "YearInitial": {
                            "type": "integer"
                        },
                        "gene_id": {
                            "type": "integer"
                        },
                        "gene_name": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "pubmed": {
                            "type": "integer"
                        },
                        "score": {
                            "type": "float"
                        },
                        "source": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        }
                    }
                },
                "variants_related_to_disease": {
                    "properties": {
                        "DPI": {
                            "type": "float"
                        },
                        "DSI": {
                            "type": "float"
                        },
                        "EI": {
                            "type": "float"
                        },
                        "YearFinal": {
                            "type": "integer"
                        },
                        "YearInitial": {
                            "type": "integer"
                        },
                        "chrom": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "pos": {
                            "type": "integer"
                        },
                        "pubmed": {
                            "type": "integer"
                        },
                        "rsid": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "score": {
                            "type": "float"
                        },
                        "source": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        }
                    }
                },
                "xrefs": {
                    "properties": {
                        "disease_name": {
                            "type": "text"
                        },
                        "doid": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer",
                            "copy_to": [
                                "all"
                            ]
                        },
                        "efo": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "hp": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "icd10": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "icd10cm": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "icd9": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "mesh": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer",
                            "copy_to": [
                                "all"
                            ]
                        },
                        "mondo": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer",
                            "copy_to": [
                                "all"
                            ]
                        },
                        "nci": {
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
                        "umls": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer",
                            "copy_to": [
                                "all"
                            ]
                        }
                    }
                }
            }
        }
    }
    return mapping
