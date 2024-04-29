def get_customized_mapping(cls):
    mapping = {
        "ctd": {
            "properties": {
                "chemical_related_to_disease": {
                    "properties": {
                        "cas_registry_number": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "chemical_name": {
                            "type": "text"
                        },
                        "direct_evidence": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "mesh_chemical_id": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "pubmed": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "source": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        }
                    }
                },
                "mesh": {
                    "type": "keyword",
                    "normalizer": "keyword_lowercase_normalizer",
                    "copy_to": [
                        "all"
                    ]
                },
                "omim": {
                    "type": "keyword",
                    "normalizer": "keyword_lowercase_normalizer",
                    "copy_to": [
                        "all"
                    ]
                },
                "pathway_related_to_disease": {
                    "properties": {
                        "inference_gene_symbol": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "kegg_pathway_id": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "pathway_name": {
                            "type": "text"
                        },
                        "react_pathway_id": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        },
                        "source": {
                            "type": "keyword",
                            "normalizer": "keyword_lowercase_normalizer"
                        }
                    }
                }
            }
        }
    }
    return mapping
