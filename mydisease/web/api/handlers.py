# -*- coding: utf-8 -*-
from biothings.web.api.es.handlers import BiothingHandler
from biothings.web.api.es.handlers import MetadataHandler
from biothings.web.api.es.handlers import QueryHandler
from biothings.web.api.es.handlers import StatusHandler

class DiseaseHandler(BiothingHandler):
    ''' This class is for the /disease endpoint. '''
    pass

class QueryHandler(QueryHandler):
    ''' This class is for the /query endpoint. '''
    pass

class StatusHandler(StatusHandler):
    ''' This class is for the /status endpoint. '''
    pass

"""class FieldsHandler(FieldsHandler):
    ''' This class is for the /metadata/fields endpoint. '''
    pass"""

class MetadataHandler(MetadataHandler):
    ''' This class is for the /metadata endpoint. '''
    pass
