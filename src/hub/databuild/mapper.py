import biothings.utils.mongo as mongo
from biothings.hub.databuild.mapper import IDBaseMapper


class CanonicalIDMapper(IDBaseMapper):
    """
    A mapper to convert any disease document _id into the canonical ID
    using the compendia_disease and compendia_phenotypic_feature reference collections.
    """

    def load(self):
        if self.map is None:
            self.map = {}
            self.mapping_source = {}
            # Load mappings from compendia_disease first.
            disease_col = mongo.get_src_db()["compendia_disease"]
            for doc in disease_col.find({}, {"_id": 1, "identifiers.i": 1}):
                canonical = doc["_id"]
                for ident in doc.get("identifiers", []):
                    alias = ident.get("i")
                    if alias:
                        self.map[alias] = canonical
                        self.mapping_source[alias] = "disease"

            # Now load mappings from compendia_phenotypic_feature for missing aliases.
            phenotypic_col = mongo.get_src_db()["compendia_phenotypic_feature"]
            for doc in phenotypic_col.find({}, {"_id": 1, "identifiers.i": 1}):
                canonical = doc["_id"]
                for ident in doc.get("identifiers", []):
                    alias = ident.get("i")
                    if alias and alias not in self.map:
                        self.map[alias] = canonical
                        self.mapping_source[alias] = "phenotypic"
