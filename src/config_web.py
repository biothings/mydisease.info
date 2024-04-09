import re

# *****************************************************************************
# Elasticsearch variables
# *****************************************************************************
ES_HOST = "http://localhost:9200"
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


disease_prefix_handling = [
    # Matches MONDO IDs (MONDO:xxxx) regardless of case
    (
        re.compile(r"MONDO\:[0-9]+", re.I),
        (
            "mondo.mondo",
            "_id",
            "disgenet.xrefs.mondo",
            "disease_ontology.xrefs.mondo",
            "mondo.xrefs.mondo",
        ),
    ),
    # Matches MESH IDs (e.g., "MESH:XXXX") or no-prefix IDs starting with "D" or "C" followed by digits (e.g., "D000086382", "C5203670").
    (
        re.compile(r"([DC][0-9]+|MESH\:[A-Z0-9]+)", re.I),
        (
            "mondo.xrefs.mesh",
            "_id",
            "disease_ontology.xrefs.mesh",
            "ctd.mesh",
            "disgenet.xrefs.mesh",
            "umls.mesh",
            "disease_ontology.xrefs.mesh",
            "disease_ontology.xrefs.ncit",
            "mondo.xrefs.ncit",
        ),
    ),
    # Matches Disease Ontology IDs (DOID:xxxx) regardless of case
    (
        re.compile(r"DOID\:[0-9]+", re.I),
        ("disease_ontology.doid", "disgenet.xrefs.doid", "mondo.xrefs.doid", "_id"),
    ),
    # Matches OMIM IDs (OMIM:xxxx) regardless of case or no prefix IDs with only digits
    (
        re.compile(r"(OMIM\:)?[0-9]+", re.I),
        (
            "_id",
            "ctd.omim",
            "disease_ontology.xrefs.omim",
            "disgenet.xrefs.omim",
            "hpo.omim",
            "mondo.xrefs.omim",
        ),
    ),
    # Matches HP IDs (HP:xxxx) regardless of case
    (re.compile(r"HP\:[0-9]+", re.I), ("disgenet.xrefs.hp", "mondo.xrefs.hp")),
    # Matches ORPHANET IDs (ORPHANET:xxxx) regardless of case
    (
        re.compile(r"ORPHANET\:[0-9]+", re.I),
        ("_id", "mondo.xrefs.orphanet", "hpo.orphanet"),
    ),
    # Matches UMLS IDs (UMLS:xxxx) regardless of case
    (
        re.compile(r"UMLS\:[A-Z0-9]+", re.I),
        ("_id", "mondo.xrefs.umls", "umls.umls", "disgenet.xrefs.umls"),
    ),
    # Matches DECIPHER IDs (DECIPHER:xxxx) regardless of case
    (re.compile(r"DECIPHER\:[0-9]+", re.I), ("_id", "hpo.decipher")),
    # Matches KEGG.DISEASE IDs (H00031) regardless of case NOTE KEGG.DISEASE IDs are not in the data
    (
        re.compile(r"^H\d+$", re.I),  # double check parser
        ("disease_ontology.xrefs.kegg", "mondo.xrefs.kegg"),
    ),
    # Matches ICD9 IDs (255.4) regardless of case
    (
        re.compile(r"^\d{3}(\.\d{1,2})?$", re.I),
        ("disease_ontology.xrefs.icd9", "disgenet.xrefs.icd9", "mondo.xrefs.icd9"),
    ),
    # Matches ICD10 IDs (U07.1) regardless of case
    (
        re.compile(r"^[A-Z][0-9][0-9A-Z]?(?:\.[0-9A-Z]{1,5})?$", re.I),
        ("disease_ontology.xrefs.icd10", "disgenet.xrefs.icd10", "mondo.xrefs.icd10"),
    ),
    # Matches ICD11 IDs (CA01.001) regardless of case NOTE ICD11 IDs are not in the data
    (re.compile(r"^[A-NP-Z][0-9]([0-9A-Z]{0,5})?$", re.I), "mondo.xrefs.icd11"),
]

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
    *disease_prefix_handling,
    id_disease_regex_pattern,
    default_disease_regex_pattern,
]

ANNOTATION_DEFAULT_SCOPES = ["_id", "disease_ontology.doid", "mondo.xrefs.mesh"]

STATUS_CHECK = {"id": "MONDO:0021004", "index": "mydisease_current"}
