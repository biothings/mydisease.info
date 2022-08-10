import os.path
from .parser import load_data
import biothings.hub.dataload.storage as storage
import biothings.hub.dataload.uploader as uploader


SRC_META = {
    "url": 'https://www.nlm.nih.gov/research/umls/index.html',
    "license_url": "https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release/license_agreement.html"
}


class UMLSUploader(uploader.BaseSourceUploader):

    name = "umls"
    # Try to combine duplicate documents.
    storage_class = storage.MergerStorage
    __metadata__ = {"src_meta": SRC_META}

    def load_data(self, data_folder):
        umls_docs = load_data(data_folder)
        return umls_docs

    @classmethod
    def get_mapping(cls):
        mapping = {
            "umls": {
                "properties": {
                    "icd10cm": {
                        "properties": {
                            "preferred": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "non-preferred": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "snomed": {
                        "properties": {
                            "preferred": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "non-preferred": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "umls": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                        "copy_to": ["all"]
                    },
                    "icd10am": {
                        "properties": {
                            "non-preferred": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "preferred": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "icd10": {
                        "properties": {
                            "non-preferred": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "preferred": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "mesh": {
                        "properties": {
                            "preferred": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "non-preferred": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "nci": {
                        "properties": {
                            "preferred": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "non-preferred": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "icd9cm": {
                        "properties": {
                            "preferred": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "non-preferred": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    }
                }
            }
        }
        return mapping
