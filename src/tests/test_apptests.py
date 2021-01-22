import glob
import json
import os

import pytest
import elasticsearch
from biothings.tests.web import BiothingsWebAppTest


class TestMyDiseaseConfigDefaultScopes(BiothingsWebAppTest):
    TEST_DATA_NAME = 'DefaultScopes'

    def _process_es_data_dir(self, data_dir_path):
        if not os.path.exists(data_dir_path):
            yield
            return

        client = elasticsearch.Elasticsearch(self.settings.ES_HOST)
        server_major_version = client.info()['version']['number'].split('.')[0]
        client_major_version = str(elasticsearch.__version__[0])
        if server_major_version != client_major_version:
            pytest.exit('ES version does not match its python library.')

        # FIXME: this is broken
        default_doc_type = self.settings.ES_DOC_TYPE

        indices = []
        glob_json_pattern = os.path.join(data_dir_path, '*.json')
        # FIXME: wrap around in try-finally so the index is guaranteed to be
        #  cleaned up
        for index_mapping_path in glob.glob(glob_json_pattern):
            index_name = os.path.basename(index_mapping_path)
            index_name = os.path.splitext(index_name)[0]
            indices.append(index_name)
            if client.indices.exists(index_name):
                raise Exception(f"{index_name} already exists!")
            with open(index_mapping_path, 'r') as f:
                mapping = json.load(f)
            data_path = os.path.join(data_dir_path, index_name + '.ndjson')
            with open(data_path, 'r') as f:
                bulk_data = f.read()
            if elasticsearch.__version__[0] > 6:
                client.indices.create(index_name, mapping, include_type_name=True)
                client.bulk(bulk_data, index_name)
            else:
                client.indices.create(index_name, mapping)
                # FIXME: doc_type problem in ES6
                # client.bulk(bulk_data, index_name, default_doc_type)
                client.bulk(bulk_data, index_name, "disease")

            client.indices.refresh()
        yield
        for index_name in indices:
            client.indices.delete(index_name)

    @pytest.fixture(scope="class", autouse=True)
    def load_es_data_cls(self, request):
        if self.TEST_DATA_NAME is not None:
            data_dir = self.TEST_DATA_NAME
        else:
            data_dir = request.cls.__name__
        data_dir = os.path.join('./test_data/', data_dir)

        yield from self._process_es_data_dir(data_dir)

    # reason why we do not want this is because this would screw up
    # the indices loaded for the class/session/module
    # @pytest.fixture(scope="function", autouse=True)
    # def load_es_data_fn(self, request):
    #     data_dir = './test_data/' + request.cls.__name__ + '/' + \
    #         request.function.__name__
    #     yield from self._process_es_data_dir(data_dir)

    def test_010_id(self):
        q = 'mock0'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['_id'].lower() == q

    def test_011_doid(self):
        q = 'doid:0'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['disease_ontology']['doid'].lower() == q

    def test_012_mesh(self):
        q = 'd0'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['mondo']['xrefs']['mesh'].lower() == q

    def test_020_does_not_search_all(self):
        q = 'doid:1'  # mondo.xrefs.doid is copied to all
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert res[0]['notfound']
