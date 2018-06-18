mapping = {
    "disgenet": {
        "properties": {
            "genes_related_to_disease": {
                "properties": {
                    "gene_id": {
                        "type": "integer"
                    },
                    "gene_name": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "n_pmids": {
                        "type": "integer"
                    },
                    "n_snps": {
                        "type": "integer"
                    },
                    "score": {
                        "type": "float"
                    },
                    "source": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    }
                }
            },
            "variants_related_to_disease": {
                "properties": {
                    "rsid": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "chrom": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "pos": {
                        "type": "integer"
                    },
                    "pubmed": {
                        "type": "integer"
                    },
                    "score": {
                        "type": "float"
                    },
                    "source": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "description": {
                        "type": "text",
                        "index": False
                    }
                }
            },
            "xrefs": {
                "properties": {
                    "disease_name": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "nci": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "umls": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "hp": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "icd9": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "omim": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "doid": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "efo": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "mesh": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "ordo": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    }
                }
            }
        }
    }
}
