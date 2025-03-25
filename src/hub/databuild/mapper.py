import biothings.utils.mongo as mongo
from biothings.hub.databuild.mapper import BaseMapper


class CanonicalIDMapper(BaseMapper):
    def __init__(self, *args, **kwargs):
        super(CanonicalIDMapper, self).__init__(*args, **kwargs)
        self.alias_to_canonical = None  # cache dict

    def load(self):
        """Load the mapping from compendia_disease once into memory."""
        if self.alias_to_canonical is None:
            col = mongo.get_src_db()["compendia_disease"]
            # Build a mapping from each alternate identifier to the canonical _id
            self.alias_to_canonical = {}
            for ref_doc in col.find({}, {"identifiers.i": 1}):
                canon_id = ref_doc["_id"]
                for ident in ref_doc.get("identifiers", []):
                    alias = ident.get("i")
                    if alias:
                        self.alias_to_canonical[alias] = canon_id

    def process(self, docs):
        """Replace _id with canonical ID if a mapping exists."""
        for doc in docs:
            orig_id = doc["_id"]
            new_id = self.alias_to_canonical.get(orig_id)
            if new_id:
                doc["_id"] = new_id  # update to canonical
            yield doc
