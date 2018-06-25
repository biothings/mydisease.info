import os

from mydisease import DATA_DIR

__METADATA__ = {
    "src_name": 'CTD',
    "src_url": 'http://ctdbase.org/downloads/',
    "field": "ctd",
    "license": "unknown",
    "license_url": "http://ctdbase.org/about/legal.jsp"
}

# downloaded from: http://www.disgenet.org/web/DisGeNET/menu/downloads

# The files contains disease-go associations from CTD.
url_disease_go_bp = "http://ctdbase.org/reports/CTD_Disease-GO_biological_process_associations.csv.gz"
file_path_disease_go_bp = os.path.join(DATA_DIR, "CTD_Disease-GO_biological_process_associations.csv.gz")

url_disease_go_cc = "http://ctdbase.org/reports/CTD_Disease-GO_cellular_component_associations.csv.gz"
file_path_disease_go_cc = os.path.join(DATA_DIR, "CTD_Disease-GO_cellular_component_associations.csv.gz")

url_disease_go_mf = "http://ctdbase.org/reports/CTD_Disease-GO_molecular_function_associations.csv.gz"
file_path_disease_go_mf = os.path.join(DATA_DIR, "CTD_Disease-GO_molecular_function_associations.csv.gz")

# The files contains disease-pathway associations from CTD.
url_disease_pathway = "http://ctdbase.org/reports/CTD_diseases_pathways.csv.gz"
file_path_disease_pathway = os.path.join(DATA_DIR, "CTD_diseases_pathways.csv.gz")

# The files contains disease-chemical associations from CTD.
url_disease_chemical = "http://ctdbase.org/reports/CTD_chemicals_diseases.csv.gz"
file_path_disease_chemical = os.path.join(DATA_DIR, "CTD_chemicals_diseases.csv.gz")

# mondo mapping file
url_mondo = "http://purl.obolibrary.org/obo/mondo.json"
file_path_mondo = os.path.join(DATA_DIR, "mondo.json")

