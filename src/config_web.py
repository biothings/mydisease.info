
# *****************************************************************************
# Elasticsearch variables
# *****************************************************************************
# elasticsearch server transport url
ES_HOST = 'es6.biothings.io'
# elasticsearch index name
ES_INDEX = 'mydisease_current'
# elasticsearch document type
ES_DOC_TYPE = 'disease'

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
    'index': 'mydisease_current',
    'doc_type': 'disease'
}
    
