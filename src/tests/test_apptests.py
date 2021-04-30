import glob
import json
import os

import pytest
import elasticsearch
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
        assert q in [x.lower() for x
                     in self.get_all_nested(res[0], 'disease_ontology.doid')]

    def test_012_mesh(self):
        q = 'c579991'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert q in [x.lower() for x
                     in self.get_all_nested(res[0], 'mondo.xrefs.mesh')]

    def test_020_does_not_search_all(self):
        q = 'DOID:0060208'  # mondo.xrefs.doid is copied to all
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert res[0]['notfound']
