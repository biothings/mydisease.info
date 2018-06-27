import os

from mydisease import DATA_DIR

__METADATA__ = {
    "src_name": 'HPO',
    "src_url": 'https://hpo.jax.org/app/download/annotation',
    "field": "hpo",
    "license": "unknown",
    "license_url": "https://hpo.jax.org/app/license"
}


# The files contains disease-hpo associations from HPO.
url_disease_hpo = "http://compbio.charite.de/jenkins/job/hpo.annotations.2018/"
file_path_disease_hpo = os.path.join(DATA_DIR, "phenotype.hpoa")

# mondo mapping file
url_mondo = "http://purl.obolibrary.org/obo/mondo.json"
file_path_mondo = os.path.join(DATA_DIR, "mondo.json")

