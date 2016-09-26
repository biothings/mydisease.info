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
url_snp_disease = "http://www.disgenet.org/ds/DisGeNET/results/all_snps_sentences_pubmeds.tsv.gz"
file_path_snp_disease = os.path.join(DATA_DIR, "all_snps_sentences_pubmeds.tsv.gz")

jsonld = {
    "disgenet": {
        "@context": {"genes": "",
                     "snps": ""}
    },
    "disgenet/genes": {
        "@context": {
            "gene_id": "http://identifiers.org/ncbigene/",
            "gene_name": "http://identifiers.org/orphanet.ordo/"
        }
    },
    "disgenet/snps": {
        "@context": {
            "rsid": "http://identifiers.org/dbsnp/",
            "gene_name": "http://identifiers.org/orphanet.ordo/"
        }
    }

}
