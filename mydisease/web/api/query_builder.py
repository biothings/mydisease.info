# -*- coding: utf-8 -*-
from biothings.web.api.es.query_builder import ESQueryBuilder


class ESQueryBuilder(ESQueryBuilder):
    def _return_query_kwargs(self, query_kwargs):
        _kwargs = super()._return_query_kwargs(query_kwargs)
        # del _kwargs["doc_type"]
        return _kwargs
