
# *****************************************************************************
# Elasticsearch variables
# *****************************************************************************
ES_HOST = 'es7.biothings.io:443'
ES_ARGS = dict(aws=True)
ES_INDICES = dict(disease='mydisease_current')

# *****************************************************************************
# Web Application
# *****************************************************************************
API_VERSION = 'v1'

# *****************************************************************************
# Analytics & Features
# *****************************************************************************

GA_ACTION_QUERY_GET = 'query_get'
GA_ACTION_QUERY_POST = 'query_post'
GA_ACTION_ANNOTATION_GET = 'disease_get'
GA_ACTION_ANNOTATION_POST = 'disease_post'
GA_TRACKER_URL = 'MyDisease.info'

STATUS_CHECK = {
    'id': 'MONDO:0021004',
    'index': 'mydisease_current'
}

ANNOTATION_DEFAULT_SCOPES = [
    '_id', 'disease_ontology.doid', 'mondo.xrefs.mesh'
]
