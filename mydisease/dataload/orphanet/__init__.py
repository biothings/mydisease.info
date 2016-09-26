import os
from mydisease import DATA_DIR

__METADATA__ = {
    "src_name": 'Orphanet',
    "src_url": 'http://www.orpha.net/consor/cgi-bin/index.php',
    "release": "V2.2",
    "field": "orphanet",
    "license": "CC-BY-ND 3.0",
    "license_url": "http://www.orphadata.org/cgi-bin/inc/legal.inc.php"
}

# downloaded from: http://www.orphadata.org/cgi-bin/index.php

# http://www.orphadata.org/cgi-bin/inc/ordo_orphanet.inc.php
ordo_url = "http://data.bioontology.org/ontologies/ORDO/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv"
ordo_path = os.path.join(DATA_DIR, "ORDO.csv.gz")

# http://www.orphadata.org/cgi-bin/inc/product1.inc.php
# Rare diseases and cross-referencing
xref_url = "http://www.orphadata.org/data/xml/en_product1.xml"
xref_path = os.path.join(DATA_DIR, os.path.split(xref_url)[1])

# http://www.orphadata.org/cgi-bin/inc/product2.inc.php
# Rare diseases epidemiological data
# Point prevalence, prevalence at birth, lifetime prevalence, annual incidence, number of cases an/or families
prev_url = "http://www.orphadata.org/data/xml/en_product2_prev.xml"
prev_path = os.path.join(DATA_DIR, os.path.split(prev_url)[1])
# Type of inheritance, average age of onset and average age of death
ages_url = "http://www.orphadata.org/data/xml/en_product2_ages.xml"
ages_path = os.path.join(DATA_DIR, os.path.split(ages_url)[1])

# http://www.orphadata.org/cgi-bin/inc/product4.inc.php
# Phenotypes associated with rare disorders
hpo_url = "http://www.orphadata.org/data/xml/en_product4_HPO.xml"
hpo_path = os.path.join(DATA_DIR, os.path.split(hpo_url)[1])

# http://www.orphadata.org/cgi-bin/inc/product6.inc.php
# Rare diseases with their associated genes
gene_url = "http://www.orphadata.org/data/xml/en_product6.xml"
gene_path = os.path.join(DATA_DIR, os.path.split(gene_url)[1])