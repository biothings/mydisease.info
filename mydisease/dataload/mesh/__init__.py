import os

from mydisease import DATA_DIR

__METADATA__ = {
    "src_name": 'MeSH',
    "src_url": 'https://www.nlm.nih.gov/mesh/',
    "version": "2016",
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


def get_mapping():
    mapping = {
        "mesh": {
            "properties": {
                "_id": {
                    "type": "string"
                },
                "record_type": {
                    "type": "string"
                },
                "note": {
                    "type": "string"
                },
                "semantic_type_id": {
                    "type": "string"
                },
                "term": {
                    "type": "string"
                },
                "see_also": {
                    "type": "string"
                },
                "last_updated": {
                    "type": "string"
                },
                "synonyms": {
                    "type": "string"
                },
                "descriptor_class": {
                    "type": "string"
                },
                "semantic_type": {
                    "type": "string"
                },
                "tree": {
                    "type": "string"
                }
            }
        }
    }
    return mapping
