from biothings.tests.web import BiothingsWebTest


class MyDiseaseWebTestBase(BiothingsWebTest):
    host ='mydisease.info'


class TestMyDiseaseDataIntegrity(MyDiseaseWebTestBase):
    ##################
    # Query Endpoint #
    ##################

    def test_010_id(self):
        q = 'MONDO:0010936'
        res = self.request("query", method="POST", data={"q": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['_id'].lower() == q.lower()

    def test_011_doid(self):
        q = '0111227'
        res = self.request("query", method="GET", data={"q": q})
        res = res.json()
        assert len(res['hits']) == 1
        assert self.value_in_result(q, res, 'hits.disease_ontology.doid', True)

    def test_012_mesh(self):
        q = 'c579991'
        res = self.request("query", method="GET", data={"q": q})
        res = res.json()
        assert len(res['hits']) == 1
        assert self.value_in_result(q, res, 'hits.mondo.xrefs.mesh', True)

    def test_014_omim(self):
        q = '618646'
        res = self.request("query", method="GET", data={"q": q})
        res = res.json()
        assert len(res['hits']) == 1
        assert self.value_in_result(q, res, 'hits.hpo.omim', True)

    def test_020_does_not_search_all(self):
        q = 'DOID:0060208'  # mondo.xrefs.doid is copied to all
        res = self.request("query", method="POST", data={"q": q})
        res = res.json()
        assert res[0]['notfound']

    def test_021_fielded_query(self):
        q = 'MONDO:0010936'
        res = self.request("query", method="POST", data={"q": q, "fields": "mondo.definition"})
        res = res.json()
        assert len(res) == 1
        assert 'mondo' in res[0]
        assert 'definition' in res[0]['mondo']

    #######################
    # Annotation Endpoint #
    #######################

    def test_040_id(self):
        q = 'MONDO:0010936'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['_id'].lower() == q.lower()

    def test_041_doid(self):
        q = 'doid:0111227'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(q, res, 'disease_ontology.doid', True)

    def test_042_mesh(self):
        q = 'c579991'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(q, res, 'mondo.xrefs.mesh', True)

    def test_050_does_not_search_all(self):
        q = 'DOID:0060208'  # mondo.xrefs.doid is copied to all
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert res[0]['notfound']

    def test_60_multiple_ids(self):
        q = 'MONDO:0010936,MONDO:0010937'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 2
        assert res[0]['_id'].lower() == 'mondo:0010936'
        assert res[1]['_id'].lower() == 'mondo:0010937'

    def test_070_fielded_query(self):
        q = 'MONDO:0010936'
        res = self.request("disease", method="POST", data={"ids": q, "fields": "mondo.definition"})
        res = res.json()
        assert len(res) == 1
        assert 'mondo' in res[0]
        assert 'definition' in res[0]['mondo']

