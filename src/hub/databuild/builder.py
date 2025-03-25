from biothings.hub.databuild.builder import DataBuilder
from biothings.hub.dataload.storage import UpsertStorage
from biothings.utils.mongo import doc_feeder, get_target_db

from .mapper import CanonicalIDMapper


def merge_docs_array(doc1, doc2):
    """
    Merge two documents by combining fields as arrays.
    For any key (other than '_id') that exists in both documents, if the field is not
    already a list, convert it to a list and append the new value.
    """
    merged = {}
    # We assume both docs share the same _id
    merged["_id"] = doc1["_id"]

    # Get all keys from both documents except '_id'
    all_keys = set(doc1.keys()) | set(doc2.keys())
    all_keys.discard("_id")

    for key in all_keys:
        v1 = doc1.get(key)
        v2 = doc2.get(key)

        if v1 is None:
            merged[key] = v2
        elif v2 is None:
            merged[key] = v1
        else:
            # If both have a value for this key:
            if isinstance(v1, list):
                # v1 is already a list; append v2 (or extend if it's also a list)
                if isinstance(v2, list):
                    merged[key] = v1 + v2
                else:
                    merged[key] = v1 + [v2]
            else:
                # v1 is not a list
                if isinstance(v2, list):
                    merged[key] = [v1] + v2
                else:
                    # Neither is a list, so wrap both in a list
                    merged[key] = [v1, v2]
    return merged


class CanonicalDataBuilder(DataBuilder):
    def post_merge(self, source_names, batch_size, job_manager):
        # Instantiate and load your canonical mapper.
        mapper = CanonicalIDMapper(name="canonical")
        mapper.load()

        db = get_target_db()
        orig_col = self.target_backend.target_collection
        temp_col_name = orig_col.name + "_temp"

        # Create an instance of UpsertStorage for the temporary collection.
        storage = UpsertStorage(db, temp_col_name, self.logger)

        # Process documents in batches from the original merged collection.
        for docs in doc_feeder(orig_col, step=batch_size, inbatch=True):
            merged_docs = {}
            for doc in docs:
                # Look up the canonical id. If no mapping is found, keep the original.
                new_id = mapper.map.get(doc["_id"], doc["_id"])
                doc["_id"] = new_id  # update _id in the document
                if new_id in merged_docs:
                    # Merge the current document with the one already present using our array-based merge.
                    merged_docs[new_id] = merge_docs_array(
                        merged_docs[new_id], doc)
                else:
                    merged_docs[new_id] = doc
            # Use UpsertStorage to process this batch of merged documents.
            if merged_docs:
                # Convert dict_values to list to avoid the "no attribute 'items'" error.
                storage.process(list(merged_docs.values()),
                                batch_size=batch_size)

        # After processing all batches, drop the original collection and rename the temporary one.
        orig_col.drop()
        db[temp_col_name].rename(orig_col.name)
        self.logger.info(
            "Canonical ID mapping completed; new collection is '%s'", orig_col.name)

    def get_stats(self, sources, job_manager):
        self.logger.info("Computing canonical mapping statistics...")
        meta = {"__REPLACE__": True}
        col = self.target_backend.target_collection
        meta["total_documents"] = col.count_documents({})
        self.logger.info("Canonical mapping stats: %s", meta)
        return meta
