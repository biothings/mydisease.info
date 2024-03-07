"""
Tests for exercising the CURIE ID querying capabilities for
the mydisease instance

Tests attempt to verify that queries leveraging the CURIE ID syntax
should return the same documents as queries that don't but logically
should return the same documents
"""

import logging

import pytest
import requests

from biothings.tests.web import BiothingsDataTest

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TestMyDiseaseCurieIdParsing(BiothingsDataTest):
    host = "mydisease.info"
    prefix = "v1"

    @pytest.mark.xfail(
        reason="CURIE ID SUPPORT NOT CURRENTLY ENABLED ON MYDISEASE.INFO HOST",
        run=True,
        strict=True,
    )
    def test_001_curie_id_annotation_endpoint_GET(self):
        """
        Tests the annotation endpoint support for the biolink CURIE ID.

        If support is enabled then we should retrieve the exact same document
        for all the provided queries

        A mirror copy of the tests we have in the biothings_client
        package (disease.py)
        """
        curie_id_testing_collection = [
            ("MONDO:0010936", "MONDO:MONDO:0010936", "mondo.mondo:MONDO:0010936"),
            ("MONDO:0010936", "mondo:MONDO:0010936", "mondo.mondo:MONDO:0010936"),
            ("MONDO:0010936", "MoNdO:MONDO:0010936", "mondo.mondo:MONDO:0010936"),
            (
                "MONDO:0010936",
                "DOID:DOID:0111227",
                "disease_ontology.doid:DOID:0111227",
            ),
            (
                "MONDO:0010936",
                "doid:DOID:0111227",
                "disease_ontology.doid:DOID:0111227",
            ),
            (
                "MONDO:0010936",
                "DoID:DOID:0111227",
                "disease_ontology.doid:DOID:0111227",
            ),
        ]

        aggregation_query_groups = []
        endpoint = "disease"
        for query_collection in curie_id_testing_collection:
            query_result_storage = []
            for similar_query in query_collection:
                query_result = self.request(f"{endpoint}/{similar_query}", expect=200)
                assert isinstance(query_result, requests.models.Response)
                assert query_result.url == self.get_url(
                    path=f"{endpoint}/{similar_query}"
                )
                query_result_storage.append(query_result.json())

            results_aggregation = [
                query == query_result_storage[0] for query in query_result_storage[1:]
            ]

            if all(results_aggregation):
                logger.info(f"Query group {query_collection} succeeded")
            else:
                logger.info(f"Query group {query_collection} failed")

            aggregation_query_groups.append(all(results_aggregation))
        assert all(aggregation_query_groups)

    @pytest.mark.xfail(
        reason="CURIE ID SUPPORT NOT CURRENTLY ENABLED ON MYDISEASE.INFO HOST",
        run=True,
        strict=True,
    )
    def test_002_curie_id_annotation_endpoint_POST(self):
        """
        Tests the annotations endpoint support for the biolink CURIE ID.

        Batch query testing against the POST endpoint to verify that the CURIE ID can work with
        multiple

        If support is enabled then we should retrieve the exact same document for all the provided
        queries

        A mirror copy of the tests we have in the biothings_client
        package (disease.py)
        """
        curie_id_testing_collection = [
            ("MONDO:0010936", "MONDO:MONDO:0010936", "mondo.mondo:MONDO:0010936"),
            ("MONDO:0010936", "mondo:MONDO:0010936", "mondo.mondo:MONDO:0010936"),
            ("MONDO:0010936", "MoNdO:MONDO:0010936", "mondo.mondo:MONDO:0010936"),
            (
                "MONDO:0010936",
                "DOID:DOID:0111227",
                "disease_ontology.doid:DOID:0111227",
            ),
            (
                "MONDO:0010936",
                "doid:DOID:0111227",
                "disease_ontology.doid:DOID:0111227",
            ),
            (
                "MONDO:0010936",
                "DoID:DOID:0111227",
                "disease_ontology.doid:DOID:0111227",
            ),
        ]

        results_aggregation = []
        endpoint = "disease"
        for id_query, biothings_query, biolink_query in curie_id_testing_collection:
            base_result = self.request(f"{endpoint}/{id_query}", expect=200)

            query_collection = (id_query, biothings_query, biolink_query)
            delimiter = ","
            data_mapping = {
                "ids": delimiter.join([f'"{query}"' for query in query_collection])
            }
            query_results = self.request(
                endpoint, method="POST", data=data_mapping
            ).json()
            assert len(query_results) == len(query_collection)

            batch_id_query = query_results[0]
            batch_biothings_query = query_results[1]
            batch_biolink_query = query_results[2]

            batch_id_query_return_value = batch_id_query.pop("query")
            assert batch_id_query_return_value == str(id_query)

            batch_biothings_query_return_value = batch_biothings_query.pop("query")
            assert batch_biothings_query_return_value == str(biothings_query)

            batch_biolink_query_return_value = batch_biolink_query.pop("query")
            assert batch_biolink_query_return_value == str(biolink_query)

            batch_result = (
                base_result.json() == batch_id_query,
                base_result.json() == batch_biothings_query,
                base_result.json() == batch_biolink_query,
            )
            results_aggregation.append(batch_result)

        results_validation = []
        failure_messages = []
        for result, test_query in zip(results_aggregation, curie_id_testing_collection):
            cumulative_result = all(result)
            if not cumulative_result:
                failure_messages.append(
                    f"Query Failure: {test_query} | Results: {result}"
                )
            results_validation.append(cumulative_result)

        assert all(results_validation), "\n".join(failure_messages)
        assert all(results_validation), "\n".join(failure_messages)
