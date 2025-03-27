from biothings.hub.databuild.builder import DataBuilder
from biothings.utils.mongo import doc_feeder, get_target_db
from pymongo import ReplaceOne

from .mapper import CanonicalIDMapper


class CanonicalDataBuilder(DataBuilder):
    def merge_docs_array(self, doc1, doc2):
        """
        Merge two documents by combining fields as arrays.
        For any key (other than '_id') that exists in both documents, if the field is not
        already a list, convert it to a list and append the new value.
        """
        merged = {}
        merged["_id"] = doc1["_id"]
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
                if isinstance(v1, list):
                    merged[key] = v1 + \
                        v2 if isinstance(v2, list) else v1 + [v2]
                else:
                    merged[key] = [v1] + \
                        v2 if isinstance(v2, list) else [v1, v2]
        return merged

    def post_merge(self, source_names, batch_size, job_manager):
        # Instantiate and load the canonical mapper.
        mapper = CanonicalIDMapper(name="canonical")
        mapper.load()

        # Initialize counters for mapping sources.
        disease_count = 0
        phenotypic_count = 0

        db = get_target_db()
        orig_col = self.target_backend.target_collection
        temp_col_name = orig_col.name + "_temp"
        temp_col = db[temp_col_name]

        # Process documents in batches from the original merged collection.
        for docs in doc_feeder(orig_col, step=batch_size, inbatch=True):
            merged_docs = {}
            for doc in docs:
                original_id = doc["_id"]
                if original_id.startswith("C"):
                    # Add UMLS prefix to canonical IDs from compendia_disease.
                    original_id = "UMLS:" + original_id
                elif original_id.startswith("ORPHANET"):
                    # Make lowercase for canonical IDs from compendia_phenotypic_feature.
                    original_id = original_id.lower()
                new_id = mapper.map.get(original_id, original_id)
                # If a mapping was applied, count it by source.
                if new_id != original_id:
                    source = mapper.mapping_source.get(original_id)
                    if source == "disease":
                        disease_count += 1
                    elif source == "phenotypic":
                        phenotypic_count += 1

                doc["_id"] = new_id  # update _id in the document

                if new_id in merged_docs:
                    merged_docs[new_id] = self.merge_docs_array(
                        merged_docs[new_id], doc)
                else:
                    merged_docs[new_id] = doc

            if merged_docs:
                ops = [ReplaceOne({"_id": doc["_id"]}, doc, upsert=True)
                       for doc in merged_docs.values()]
                if ops:
                    temp_col.bulk_write(ops)

        # After processing all batches, drop the original collection and rename the temporary one.
        orig_col.drop()
        temp_col.rename(orig_col.name)
        self.logger.info(
            "Canonical ID mapping completed; new collection is '%s'", orig_col.name)
        self.logger.info(
            "Total canonical mappings applied: %d from compendia_disease and %d from compendia_phenotypic_feature",
            disease_count, phenotypic_count
        )

    def get_stats(self, sources, job_manager):
        self.logger.info("Computing canonical mapping statistics...")
        meta = {"__REPLACE__": True}
        col = self.target_backend.target_collection
        meta["total_documents"] = col.count_documents({})
        self.logger.info("Canonical mapping stats: %s", meta)
        return meta
