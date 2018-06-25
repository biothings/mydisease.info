mapping = {
    "ctd": {
        "properties": {
            "chemical_related_to_disease": {
                "properties": {
                    "cas_registry_number": {
                        "type": "text"
                    },
                    "inference_gene_symbol": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "chemical_name": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "mesh_chemical_id": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "inference_score": {
                        "type": "float"
                    },
                    "pubmed": {
                        "type": "text"
                    },
                    "direct_evidence": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "omim_id": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "source": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    }
                }
            },
            "pathway_related_to_disease": {
                "properties": {
                    "pathway_name": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "react_pathway_id": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "kegg_pathway_id": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "inference_gene_symbol": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "source": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    }
                }
            },
            "bp_related_to_disease": {
                "properties": {
                    "go_name": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "go_id": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "inference_gene_symbol": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "source": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    }
                }
            },
            "mf_related_to_disease": {
                "properties": {
                    "go_name": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "go_id": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "inference_gene_symbol": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "source": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    }
                }
            },
            "cc_related_to_disease": {
                "properties": {
                    "go_name": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "go_id": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "inference_gene_symbol": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "source": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    }
                }
            },
            "mesh": {
                "type": "text",
                "analyzer": "string_lowercase"
            },
            "omim": {
                "type": "text",
                "analyzer": "string_lowercase"
            }
        }
    }
}
