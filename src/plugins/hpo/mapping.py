def get_customized_mapping(cls):
    mapping = {
        "hpo": {
            "properties": {
                "clinical_course": {
                    "properties": {
                        "biocuration": {
                            "properties": {
                                "name": {
                                    "normalizer": "keyword_lowercase_normalizer",
                                    "type": "keyword"
                                },
                                "date": {
                                    "type": "date"
                                }
                            }
                        },
                        "evidence": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        },
                        "freq_denominator": {
                            "type": "integer"
                        },
                        "freq_numerator": {
                            "type": "integer"
                        },
                        "hpo_id": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        },
                        "hpo_name": {
                            "type": "text",
                            "copy_to": [
                                "all"
                            ]
                        },
                        "hp_freq": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        },
                        "isbn_refs": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        },
                        "numeric_freq": {
                            "type": "float"
                        },
                        "omim_refs": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        },
                        "original_disease_id": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        },
                        "orphanet_refs": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        },
                        "pmid_refs": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        }
                    }
                },
                "clinical_modifier": {
                    "properties": {
                        "biocuration": {
                            "properties": {
                                "name": {
                                    "normalizer": "keyword_lowercase_normalizer",
                                    "type": "keyword"
                                },
                                "date": {
                                    "type": "date"
                                }
                            }
                        },
                        "evidence": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        },
                        "hpo_id": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        },
                        "hpo_name": {
                            "type": "text",
                            "copy_to": [
                                "all"
                            ]
                        },
                        "hp_freq": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        },
                        "omim_refs": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        },
                        "orphanet_refs": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        },
                        "original_disease_id": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        },
                        "pmid_refs": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        }
                    }
                },
                "decipher": {
                    "type": "keyword",
                    "normalizer": "keyword_lowercase_normalizer"
                },
                "disease_name": {
                    "type": "text",
                    "copy_to": [
                        "all"
                    ]
                },
                "inheritance": {
                    "properties": {
                        "biocuration": {
                            "properties": {
                                "name": {
                                    "normalizer": "keyword_lowercase_normalizer",
                                    "type": "keyword"
                                },
                                "date": {
                                    "type": "date"
                                }
                            }
                        },
                        "evidence": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        },
                        "freq_denominator": {
                            "type": "integer"
                        },
                        "freq_numerator": {
                            "type": "integer"
                        },
                        "hpo_id": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        },
                        "hpo_name": {
                            "type": "text",
                            "copy_to": [
                                "all"
                            ]
                        },
                        "hp_freq": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        },
                        "numeric_freq": {
                            "type": "float"
                        },
                        "omim_refs": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        },
                        "original_disease_id": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        },
                        "pmid_refs": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        },
                        "website_refs": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        }
                    }
                },
                "omim": {
                    "type": "keyword",
                    "normalizer": "keyword_lowercase_normalizer",
                    "copy_to": [
                        "all"
                    ]
                },
                "orphanet": {
                    "type": "keyword",
                    "normalizer": "keyword_lowercase_normalizer",
                    "copy_to": [
                        "all"
                    ]
                },
                "phenotype_related_to_disease": {
                    "properties": {
                        "biocuration": {
                            "properties": {
                                "name": {
                                    "normalizer": "keyword_lowercase_normalizer",
                                    "type": "keyword"
                                },
                                "date": {
                                    "type": "date"
                                }
                            }
                        },
                        "clinical_modifier": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "decipher_refs": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "evidence": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "freq_denominator": {
                            "type": "integer"
                        },
                        "freq_numerator": {
                            "type": "integer"
                        },
                        "hp_freq": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "hpo_id": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "isbn_refs": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "numeric_freq": {
                            "type": "float"
                        },
                        "omim_refs": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "onset": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "original_disease_id": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword"
                        },
                        "orphanet_refs": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "pmid_refs": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "sex": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "website_refs": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        }
                    }
                }
            }
        }
    }
    return mapping
