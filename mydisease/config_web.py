# -*- coding: utf-8 -*-
from biothings.web.settings.default import *

from web.api.handlers import (DiseaseHandler, MetadataHandler, QueryHandler,
                              StatusHandler)
from web.api.query import ESQuery
from web.api.query_builder import ESQueryBuilder
from web.api.transform import ESResultTransformer

# *****************************************************************************
# Elasticsearch variables
# *****************************************************************************
# elasticsearch server transport url
ES_HOST = 'localhost:9200'
# elasticsearch index name
ES_INDEX = 'mydisease_current'
# elasticsearch document type
# ES_DOC_TYPE = '_doc'
ES_DOC_TYPE = 'disease'

API_VERSION = 'v1'

# *****************************************************************************
# App URL Patterns
# *****************************************************************************
APP_LIST = [
    (r"/status", StatusHandler),
    (r"/metadata/?", MetadataHandler),
    (r"/metadata/fields/?", MetadataHandler),
    (r"/{}/disease/(.+)/?".format(API_VERSION), DiseaseHandler),
    (r"/{}/disease/?$".format(API_VERSION), DiseaseHandler),
    (r"/{}/query/?".format(API_VERSION), QueryHandler),
    (r"/{}/metadata/?".format(API_VERSION), MetadataHandler),
    (r"/{}/metadata/fields/?".format(API_VERSION), MetadataHandler),
]

###############################################################################
#   app-specific query builder, query, and result transformer classes
###############################################################################

# *****************************************************************************
# Subclass of biothings.web.api.es.query_builder.ESQueryBuilder to build
# queries for this app
# *****************************************************************************
ES_QUERY_BUILDER = ESQueryBuilder
# *****************************************************************************
# Subclass of biothings.web.api.es.query.ESQuery to execute queries for this app
# *****************************************************************************
ES_QUERY = ESQuery
# *****************************************************************************
# Subclass of biothings.web.api.es.transform.ESResultTransformer to transform
# ES results for this app
# *****************************************************************************
ES_RESULT_TRANSFORMER = ESResultTransformer


GA_ACTION_QUERY_GET = 'query_get'
GA_ACTION_QUERY_POST = 'query_post'
GA_ACTION_ANNOTATION_GET = 'disease_get'
GA_ACTION_ANNOTATION_POST = 'disease_post'
GA_TRACKER_URL = 'MyDisease.info'

STATUS_CHECK_ID = ''
