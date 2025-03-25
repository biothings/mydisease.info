import biothings.utils.mongo as mongo
from biothings.hub.databuild.mapper import IDBaseMapper


class CanonicalIDMapper(IDBaseMapper):
    """
    A mapper to convert any disease document _id into the canonical ID
    using the compendia_disease reference collection.
    """

    def load(self):
        if self.map is None:
            self.map = {}
            # Use the source database where compendia_disease is stored.
            col = mongo.get_src_db()["compendia_disease"]
            # For each record, use its _id as the canonical ID.
            # Then map all alternate identifiers (from the 'identifiers' list)
            # to this canonical value.
            for doc in col.find({}, {"_id": 1, "identifiers.i": 1}):
                canonical = doc["_id"]
                for ident in doc.get("identifiers", []):
                    alias = ident.get("i")
                    if alias:
                        self.map[alias] = canonical
