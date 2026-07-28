import sys
import types
import unittest
from unittest import mock


biothings = types.ModuleType("biothings")
hub_mod = types.ModuleType("biothings.hub")
databuild_mod = types.ModuleType("biothings.hub.databuild")
builder_dep = types.ModuleType("biothings.hub.databuild.builder")
mapper_dep = types.ModuleType("biothings.hub.databuild.mapper")
utils_mod = types.ModuleType("biothings.utils")
mongo_mod = types.ModuleType("biothings.utils.mongo")
pymongo_mod = types.ModuleType("pymongo")


class DataBuilder:
    pass


class IDBaseMapper:
    pass


class ReplaceOne:
    pass


builder_dep.DataBuilder = DataBuilder
mapper_dep.IDBaseMapper = IDBaseMapper
mongo_mod.doc_feeder = lambda *args, **kwargs: []
mongo_mod.get_target_db = lambda: None
mongo_mod.get_src_db = lambda: None
pymongo_mod.ReplaceOne = ReplaceOne

sys.modules.update({
    "biothings": biothings,
    "biothings.hub": hub_mod,
    "biothings.hub.databuild": databuild_mod,
    "biothings.hub.databuild.builder": builder_dep,
    "biothings.hub.databuild.mapper": mapper_dep,
    "biothings.utils": utils_mod,
    "biothings.utils.mongo": mongo_mod,
    "pymongo": pymongo_mod,
})

from hub.databuild import builder as builder_module
from hub.databuild.builder import CanonicalDataBuilder


class FakeReplaceOne:
    def __init__(self, filter_, replacement, upsert=False):
        """Store the replacement operation arguments."""
        self.filter = filter_
        self.replacement = replacement
        self.upsert = upsert


class FakeCollection:
    def __init__(self, docs):
        """Create an in-memory collection with initial documents."""
        self.docs = docs
        self.ops = []

    def find(self, query):
        ids = query["_id"]["$in"]
        return [self.docs[_id] for _id in ids if _id in self.docs]

    def bulk_write(self, ops):
        self.ops.extend(ops)
        for op in ops:
            self.docs[op.filter["_id"]] = op.replacement


class TestCanonicalDataBuilder(unittest.TestCase):
    def test_upsert_merged_docs_merges_canonical_docs_across_batches(self):
        with mock.patch.object(builder_module, "ReplaceOne", FakeReplaceOne):
            builder = CanonicalDataBuilder()
            temp_col = FakeCollection({
                "MONDO:0005072": {
                    "_id": "MONDO:0005072",
                    "mondo": {
                        "mondo": "MONDO:0005072",
                        "label": "neuroblastoma",
                    },
                }
            })
            merged_docs = {
                "MONDO:0005072": {
                    "_id": "MONDO:0005072",
                    "original_id": "UMLS:C0700095",
                    "umls": {
                        "umls": "C0700095",
                    },
                }
            }

            builder.upsert_merged_docs(temp_col, merged_docs)

        self.assertEqual(len(temp_col.ops), 1)
        replacement = temp_col.ops[0].replacement
        self.assertEqual(replacement["_id"], "MONDO:0005072")
        self.assertEqual(replacement["mondo"]["mondo"], "MONDO:0005072")
        self.assertEqual(replacement["mondo"]["label"], "neuroblastoma")
        self.assertEqual(replacement["umls"]["umls"], "C0700095")
        self.assertEqual(replacement["original_id"], "UMLS:C0700095")


if __name__ == "__main__":
    unittest.main()
