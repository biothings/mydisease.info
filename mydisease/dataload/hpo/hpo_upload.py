mapping = {
    "hpo": {
        "properties": {
            "phenotype_related_to_disease": {
                "properties": {
                    "aspect": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "assigned_by": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "evidence": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "hpo_id": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "frequency": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "sex": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "qualifier": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "onset": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "modifier": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    }
                }
            },
            "orphanet": {
                "type": "text",
                "analyzer": "string_lowercase"
            },
            "omim": {
                "type": "text",
                "analyzer": "string_lowercase"
            },
            "disease_name": {
                "type": "text",
                "analyzer": "string_lowercase"
            }
        }
    }
}
