import os

from mydisease import DATA_DIR

__METADATA__ = {
    "src_name": 'DisGeNet',
    "src_url": 'http://www.disgenet.org/web/DisGeNET/menu',
    "field": "disgenet",
    "license": "ODbL",
    "license_url": "http://opendatacommons.org/licenses/odbl/"
}

# downloaded from: http://www.disgenet.org/web/DisGeNET/menu/downloads

# The file contains gene-disease associations from UNIPROT, CTD (human subset), ClinVar, Orphanet, and the GWAS Catalog.
url_gene_disease = "http://www.disgenet.org/ds/DisGeNET/results/curated_gene_disease_associations.tsv.gz"
file_path_gene_disease = os.path.join(DATA_DIR, "curated_gene_disease_associations.tsv.gz")

# The file contains All SNP-gene-disease associations in DisGeNET.
url_snp_disease = "http://www.disgenet.org/ds/DisGeNET/results/all_variant_disease_pmid_associations.tsv.gz"
file_path_snp_disease = os.path.join(DATA_DIR, "all_variant_disease_pmid_associations.tsv.gz")

# mondo mapping file
url_mondo = "http://purl.obolibrary.org/obo/mondo.json"
file_path_mondo = os.path.join(DATA_DIR, "mondo.json")

# The file contains umls mapping in DisGeNET
url_disease_mapping = "http://www.disgenet.org/ds/DisGeNET/results/disease_mappings.tsv.gz"
file_path_disease_mapping = os.path.join(DATA_DIR, "disease_mappings.tsv.gz")

