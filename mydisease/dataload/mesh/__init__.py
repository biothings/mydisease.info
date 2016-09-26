import os
from mydisease import DATA_DIR

__METADATA__ = {
    "src_name": 'MeSH',
    "src_url": 'https://www.nlm.nih.gov/mesh/',
    "release": "2016",
    "field": "mesh",
    "license": "",
    "license_url": ""
}

# downloaded from: https://www.nlm.nih.gov/mesh/download_mesh.html
# https://www.nlm.nih.gov/mesh/filelist.html
desc_url = "ftp://nlmpubs.nlm.nih.gov/online/mesh/MESH_FILES/asciimesh/d2016.bin"
supp_url = "ftp://nlmpubs.nlm.nih.gov/online/mesh/MESH_FILES/asciimesh/c2016.bin"
sem_groups = "https://semanticnetwork.nlm.nih.gov/download/SemGroups.txt"
desc_path = os.path.join(DATA_DIR, "d2016.bin")
supp_path = os.path.join(DATA_DIR, "c2016.bin")
sem_groups_path = os.path.join(DATA_DIR, "SemGroups.txt")