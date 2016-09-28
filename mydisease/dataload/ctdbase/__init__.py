import os

__METADATA__ = {
    "src_name": 'CTDBase',
    "src_url": 'http://ctdbase.org/',
    "version": "August 2016",
    "field": "ctdbase",
    "license": "custom",
    "license_url": "http://ctdbase.org/about/legal.jsp"
}

# downloaded from: http://ctdbase.org/downloads/
CTD_chemicals_diseases_url = "http://ctdbase.org/reports/CTD_chemicals_diseases.csv.gz"
CTD_genes_diseases_url = "http://ctdbase.org/reports/CTD_genes_diseases.csv.gz"
CTD_diseases_pathways_url = "http://ctdbase.org/reports/CTD_diseases_pathways.csv.gz"
CTD_Disease_GO_bp_url = "http://ctdbase.org/reports/CTD_Disease-GO_biological_process_associations.csv.gz"
CTD_Disease_GO_cc_url = "http://ctdbase.org/reports/CTD_Disease-GO_cellular_component_associations.csv.gz"
CTD_Disease_GO_mf_url = "http://ctdbase.org/reports/CTD_Disease-GO_molecular_function_associations.csv.gz"

urls = [CTD_chemicals_diseases_url, CTD_genes_diseases_url, CTD_diseases_pathways_url,
        CTD_Disease_GO_bp_url, CTD_Disease_GO_cc_url, CTD_Disease_GO_mf_url]
file_paths = [os.path.split(x)[1] for x in urls]
rlist = ["chemicals", "genes", "pathways", "GO_BP", "GO_CC", "GO_MF"]

relationships = dict(zip(rlist, file_paths))


def disease_url_format(did):
    """
    the MeSH® Unique ID or OMIM ID of the disease (e.g., “MESH:D018270” or “OMIM:211750”).
    You must include the MESH: or OMIM: database prefix.
    """
    return "http://ctdbase.org/detail.go?type=disease&acc={did}".format(did=did)


def get_mapping():
    mapping = {
        __METADATA__['field']: {
            "properties": {
                "chemicals": {
                    "properties": {
                        "casrn": {
                            "type": "string"
                        },
                        "chemical": {
                            "type": "string"
                        },
                        "inference_gene_symbol": {
                            "type": "string"
                        },
                        "inference_score": {
                            "type": "long"
                        },
                        "omim": {
                            "type": "string"
                        }
                    }
                },
                "pathways": {
                    "properties": {
                        "inference_gene_symbol": {
                            "type": "string"
                        },
                        "pathway": {
                            "type": "string"
                        }
                    }
                },
                "go_bp": {
                    "properties": {
                        "inference_gene_symbols": {
                            "type": "string"
                        },
                        "go": {
                            "type": "string"
                        }
                    }
                },
                "go_cc": {
                    "properties": {
                        "inference_gene_symbols": {
                            "type": "string"
                        },
                        "go": {
                            "type": "string"
                        }
                    }
                },
                "go_mf": {
                    "properties": {
                        "inference_gene_symbols": {
                            "type": "string"
                        },
                        "go": {
                            "type": "string"
                        }
                    }
                }

            }
        }
    }
    return mapping


jsonld = {
    "ctdbase": {
    },
    "ctdbase/chemicals": {
        "@context": {
            "casrn": "",
            "chemical": "",
            "inference_gene_symbol": "",
            "omim": "",
        }
    },
    "ctdbase/pathways": {
        "@context": {
            "inference_gene_symbol": "",
            "pathway": "",
        }
    },
    "ctdbase/go_bp": {
        "@context": {
            "inference_gene_symbols": "",
            "go": "",
        }
    },
    "ctdbase/go_cc": {
        "@context": {
            "inference_gene_symbols": "",
            "go": "",
        }
    },
    "ctdbase/go_mf": {
        "@context": {
            "inference_gene_symbols": "",
            "go": "",
        }
    },
}

"""
Chemical–disease associations
ChemicalName
ChemicalID (MeSH identifier)
CasRN (CAS Registry Number, if available)
DiseaseName
DiseaseID (MeSH or OMIM identifier)
DirectEvidence ('|'-delimited list)
InferenceGeneSymbol
InferenceScore
OmimIDs ('|'-delimited list)
PubMedIDs ('|'-delimited list)


Gene–disease associations
GeneSymbol
GeneID (NCBI Gene identifier)
DiseaseName
DiseaseID (MeSH or OMIM identifier)
DirectEvidence ('|'-delimited list)
InferenceChemicalName
InferenceScore
OmimIDs ('|'-delimited list)
PubMedIDs ('|'-delimited list)

Disease–pathway associations
DiseaseName
DiseaseID (MeSH or OMIM identifier)
PathwayName
PathwayID (KEGG or REACTOME identifier)
InferenceGeneSymbol (a gene via which the association is inferred)

GO–Disease–Gene Inference Networks
DiseaseName
DiseaseID (MeSH or OMIM identifier)
GOName
GOID (GO identifier)
InferenceGeneQty
InferenceGeneSymbols ('|'-delimited list)

"""
