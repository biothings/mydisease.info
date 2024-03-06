import re

# *****************************************************************************
# Elasticsearch variables
# *****************************************************************************
ES_HOST = "localhost:9200"
ES_ARGS = {"timeout": 60}
ES_INDICES = {"disease": "mydisease_current"}

# *****************************************************************************
# Web Application
# *****************************************************************************
API_VERSION = "v1"

# *****************************************************************************
# Features
# *****************************************************************************


# CURIE ID support based on BioLink Model
BIOLINK_MODEL_PREFIX_BIOTHINGS_GENE_MAPPING = {
    "MONDO": {"type": "disease", "field": "mondo.mondo", "keep_prefix": True},
    "DOID": {"type": "disease", "field": "disease_ontology.doid", "keep_prefix": True},
}
biolink_curie_regex_list = []
for (
    biolink_prefix,
    mapping,
) in BIOLINK_MODEL_PREFIX_BIOTHINGS_GENE_MAPPING.items():
    expression = re.compile(rf"({biolink_prefix}):(?P<term>[^:]+)", re.I)
    field_match = mapping["field"]
    pattern = (expression, field_match)
    biolink_curie_regex_list.append(pattern)

ANNOTATION_ID_REGEX_LIST = [
    *biolink_curie_regex_list,
]

ANNOTATION_DEFAULT_SCOPES = ["_id", "disease_ontology.doid", "mondo.xrefs.mesh"]

STATUS_CHECK = {"id": "MONDO:0021004", "index": "mydisease_current"}
