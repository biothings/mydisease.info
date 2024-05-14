from biothings.web.query import ESQueryBuilder
from elasticsearch_dsl import Q


class MyDiseaseQueryBuilder(ESQueryBuilder):
    def apply_extras(self, search, options):
        if options.ignore_obsolete:
            # Filter out obsolete terms (mondo.is_obsolete=True)
            search = search.filter(~Q("term", **{"mondo.is_obsolete": True}))
        return super().apply_extras(search, options)
