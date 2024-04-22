import glob
import json
import os

import elasticsearch
import pytest
from biothings.tests.web import BiothingsWebAppTest


class TestMyDiseaseConfigDefaultScopes(BiothingsWebAppTest):
    TEST_DATA_DIR_NAME = 'DefaultScopes'

    def test_010_id(self):
        q = 'MONDO:0010936'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['_id'].lower() == q.lower()

    def test_011_doid(self):
        q = 'doid:0111227'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(q, res, 'disease_ontology.doid', True)

    def test_012_mesh(self):
        q = 'c579991'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(q, res, 'mondo.xrefs.mesh', True)

    # ANNOTATION_ID_REGEX_LIST now captures DOID:0060208 in mondo.xrefs.doid. This test is no longer needed.
    # def test_020_does_not_search_all(self):
    #     q = 'DOID:0060208'  # mondo.xrefs.doid is copied to all
    #     res = self.request("disease", method="POST", data={"ids": q})
    #     res = res.json()
    #     assert res[0]['notfound']
