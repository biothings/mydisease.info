import re

# *****************************************************************************
# Elasticsearch variables
# *****************************************************************************
ES_HOST = "es8.biothings.io:9200"
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
BIOLINK_MODEL_PREFIX_BIOTHINGS_DISEASE_MAPPING = {
    "MONDO": {
        "type": "disease",
        "field": ["mondo.mondo"],
        "regex_term_pattern": "(?P<term>MONDO:[0-9]+)",
    },
    "DOID": {
        "type": "disease",
        "field": ["disease_ontology.doid"],
        "regex_term_pattern": "(?P<term>DOID:[0-9]+)",
    },
}
biolink_curie_regex_list = []
for (
    biolink_prefix,
    mapping,
) in BIOLINK_MODEL_PREFIX_BIOTHINGS_DISEASE_MAPPING.items():
    field_match = mapping.get("field", [])
    term_pattern = mapping.get("regex_term_pattern", None)
    if term_pattern is None:
        term_pattern = "(?P<term>[^:]+)"

    raw_expression = rf"({biolink_prefix}):{term_pattern}"
    compiled_expression = re.compile(raw_expression, re.I)

    pattern = (compiled_expression, field_match)
    biolink_curie_regex_list.append(pattern)

# id regex pattern
id_disease_regex_pattern = (re.compile(r"([\w]+):([0-9]+)", re.I), ["_id"])

# The default for the disease requires more care due to the potential for miscellaneous
# term values to include the ":" character. So we want to match for anything in the scope value
# up to the first ":", which end that group matching and move on to the term group matching. We then
# want to be sure we include the ":" in the value matching associated with the term for values like
# DOID:####### or MONDO:#######
default_disease_regex = re.compile(r"([^:]+):(?P<term>[\W\w]+)")
default_disease_fields = ()
default_disease_regex_pattern = (default_disease_regex, default_disease_fields)

ANNOTATION_ID_REGEX_LIST = [
    *biolink_curie_regex_list,
    id_disease_regex_pattern,
    default_disease_regex_pattern,
]

ANNOTATION_DEFAULT_SCOPES = ["_id", "disease_ontology.doid", "mondo.xrefs.mesh"]

STATUS_CHECK = {"id": "MONDO:0021004", "index": "mydisease_current"}
