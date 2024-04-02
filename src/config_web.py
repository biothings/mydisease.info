
# *****************************************************************************
# Elasticsearch variables
# *****************************************************************************
ES_HOST = 'http://localhost:9200'
ES_ARGS = dict(timeout=60)
ES_INDICES = dict(disease='mydisease_current')

# *****************************************************************************
# Web Application
# *****************************************************************************
API_VERSION = 'v1'

# *****************************************************************************
# Features
# *****************************************************************************

STATUS_CHECK = {
    'id': 'MONDO:0021004',
    'index': 'mydisease_current'
}

ANNOTATION_DEFAULT_SCOPES = [
    '_id', 'disease_ontology.doid', 'mondo.xrefs.mesh'
]
ANNOTATION_DEFAULT_REGEX_PATTERN = None
