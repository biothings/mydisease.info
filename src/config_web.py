import re

# *****************************************************************************
# Elasticsearch variables
# *****************************************************************************
ES_HOST = "http://localhost:9200"
ES_ARGS = {"request_timeout": 60}
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
            "mondo.mondo",  # Has prefix
            "mondo.xrefs.mondo",  # Has prefix
            "disgenet.xrefs.mondo",  # Has prefix
            "disease_ontology.xrefs.mondo",  # Has prefix
        ),
    ),
    # Matches MESH IDs (e.g., "MESH:XXXX") regardless of case
    (
        re.compile(r"MESH:(?P<term>[A-Z0-9]+)", re.I),
        (
            "ctd.mesh",  # No prefix
            "umls.mesh",  # No prefix
            "mondo.xrefs.mesh",  # No prefix
            "disease_ontology.xrefs.mesh",  # No prefix
            "disgenet.xrefs.mesh",  # No prefix
        ),
    ),
    # Matches NCIT IDs (NCIT:xxxx) regardless of case
    (
        re.compile(r"NCIT:(?P<term>[A-Z0-9]+)", re.I),
        (
            "mondo.xrefs.ncit",  # No prefix
            "disease_ontology.xrefs.ncit",  # No prefix
        ),
    ),
    # Matches Disease Ontology IDs (DOID:xxxx) regardless of case
    (
        re.compile(r"DOID\:[0-9]+", re.I),
        (
            "disease_ontology.doid",  # Has prefix
            "disgenet.xrefs.doid",  # Has prefix
            "mondo.xrefs.doid"  # Has prefix
        ),
    ),
    # Matches OMIM IDs (OMIM:xxxx) regardless of case
    (
        re.compile(r"OMIM:(?P<term>[0-9]+)", re.I),
        (
            "ctd.omim",  # No prefix
            "disease_ontology.xrefs.omim",  # No prefix
            "disgenet.xrefs.omim",  # No prefix
            "hpo.omim",  # No prefix
            "mondo.xrefs.omim",  # No prefix
        ),
    ),
    # Matches HP IDs (HP:xxxx) regardless of case
    (re.compile(r"HP\:[0-9]+", re.I),
     (
        "disgenet.xrefs.hp",  # Has prefix
        "mondo.xrefs.hp"  # Has prefix
    )
    ),
    # Matches ORPHANET IDs (ORPHANET:464724)
    (
        re.compile(r"ORPHANET:(?P<term>[0-9]+)", re.I),
        (
            "mondo.xrefs.orphanet",  # No prefix
            "hpo.orphanet",  # No prefix
        ),
    ),
    # Matches UMLS IDs (C0012634) regardless of case
    (
        re.compile(r"UMLS:(?P<term>[A-Z0-9]+)", re.I),
        (
            "mondo.xrefs.umls",  # No prefix
            "umls.umls",  # No prefix
            "disgenet.xrefs.umls"  # No prefix
        ),
    ),
    # Matches DECIPHER IDs (DECIPHER:xxxx) regardless of case
    (
        re.compile(r"DECIPHER:(?P<term>[0-9]+)", re.I),
        (
            "hpo.decipher"  # No prefix
        ),
    ),
    # Matches KEGG.DISEASE IDs (H00031) regardless of case
    (
        re.compile(r"KEGG:(?P<term>(H)?\d+)", re.I),
        (
            "disease_ontology.xrefs.kegg",  # No prefix, possible to have HXXXX
            # "mondo.xrefs.kegg"  # Not in the data
        ),
    ),
    # Matches ICD9 IDs (255.4) regardless of case
    (
        re.compile(r"ICD9:(?P<term>\d{3}(?:\.\d{1,2})?)", re.I),
        (
            "disease_ontology.xrefs.icd9",  # No prefix
            "disgenet.xrefs.icd9",  # No prefix
            "mondo.xrefs.icd9"  # No prefix
        ),
    ),
    # Matches ICD10 IDs (U07.1) regardless of case
    (
        re.compile(
            r"ICD10:(?P<term>[A-Z][0-9][0-9A-Z]?(?:\.[0-9A-Z]{1,5})?)", re.I),
        (
            "disease_ontology.xrefs.icd10",  # No prefix
            "disgenet.xrefs.icd10",  # No prefix
            "mondo.xrefs.icd10"  # Not in the data
        ),
    ),
    # Matches ICD11 IDs (CA01.001) regardless of case NOTE ICD11 IDs are not in the data
    (
        re.compile(r"ICD11:(?P<term>[A-NP-Z][0-9]([0-9A-Z]{0,5})?)", re.I),
        (
            "mondo.xrefs.icd11"  # Not in the data
        ),
    )
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

ANNOTATION_DEFAULT_SCOPES = [
    "_id", "disease_ontology.doid", "mondo.xrefs.mesh"]

STATUS_CHECK = {"id": "MONDO:0021004", "index": "mydisease_current"}
