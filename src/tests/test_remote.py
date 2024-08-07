import pytest
from biothings.tests.web import BiothingsWebTest


class TestMyDiseaseConfigDefaultScopes(BiothingsWebTest):
    host = 'mydisease.info'

    def test_010_id(self):
        q = 'MONDO:0010936'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['_id'] == q

    def test_011_doid(self):
        q = 'doid:0111227'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(q, res, 'disease_ontology.doid', True)

    def test_012_mesh(self):
        mesh_id = 'MESH:C579991'
        res = self.request("disease/" + mesh_id + "?fields=mondo").json()
        assert 'mondo' in res, 'No "mesh" field in response'
        assert 'xrefs' in res['mondo'], 'No "xrefs" field in response'
        assert self.value_in_result(mesh_id.split(
            ":")[1], res, 'mondo.xrefs.mesh', True)

    # Tests for "disease_ontology.doid"
    def test_013_doid_mondo_0000193(self):
        q = 'MONDO:0000193'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(
            'DOID:0090139', res, 'disease_ontology.doid', True)

    def test_014_doid_mondo_0000408(self):
        mondo_id = 'MONDO:0000408'
        res = self.request("disease/" + mondo_id +
                           "?fields=disease_ontology").json()
        assert 'disease_ontology' in res, 'No "disease_ontology" field in response'
        assert 'doid' in res['disease_ontology'], 'No "doid" field in response'
        assert self.value_in_result(
            'DOID:0050696', res, 'disease_ontology.doid', True)

    def test_015_mesh_mondo_0000253(self):
        q = 'MONDO:0000253'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(
            'D010854', res, 'mondo.xrefs.mesh', True)

    def test_016_mesh_mondo_0000485(self):
        q = 'MONDO:0000485'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(
            'D055154', res, 'mondo.xrefs.mesh', True)

    def test_017_id_mondo(self):
        q = 'MONDO:0000402'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['_id'] == q

    def test_018_id_mesh(self):
        q = 'MESH:C535501'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 2
        assert res[0]['_id'] == q

    def test_019_id_omim(self):
        q = 'OMIM:612542'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 2
        assert res[1]['_id'] == q

    def test_020_id_doid(self):
        q = 'DOID:0040018'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['_id'] == q

    def test_021_id_orphanet(self):
        orphanet_id = 'ORPHANET:90064'
        res = self.request("disease/" + orphanet_id).json()
        assert res['_id'] == orphanet_id

    def test_022_id_umls(self):
        q = 'UMLS:C0001305'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['_id'] == q

    def test_023_id_decipher(self):
        q = 'DECIPHER:2'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['_id'] == q

    def test_024_id_umls_another(self):
        q = 'UMLS:C0000735'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert res[0]['_id'] == q.split(":")[1]

    # Example for NCIT ID
    def test_ncit_id_with_prefix(self):
        q = 'NCIT:C171133'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(
            q.split(":")[1], res, 'disease_ontology.xrefs.ncit', True)

    # Example for KEGG.DISEASE ID
    def test_kegg_disease_id_with_prefix(self):
        q = 'KEGG:H00484'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(
            q.split(":")[1], res, 'disease_ontology.xrefs.kegg', True)

    # ICD10 IDs
    # prefix for icds
    def test_icd10_id_with_prefix(self):
        q = 'ICD10:U07.1'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(
            q.split(":")[1], res, 'disease_ontology.xrefs.icd10', True)

    def test_icd10_id_without_prefix(self):
        q = 'ICD10:J95.4'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(
            q.split(":")[1], res, 'disgenet.xrefs.icd10', True)

    # ICD9 IDs
    def test_icd9_id_with_prefix(self):
        q = 'ICD9:530.81'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(
            q.split(":")[1], res, 'disease_ontology.xrefs.icd9', True)

    def test_icd9_id_without_prefix(self):
        q = 'ICD9:427.41'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(
            q.split(":")[1], res, 'disgenet.xrefs.icd9', True)

    # ICD11 IDs
    @pytest.mark.skip(reason="ICD11 is not in the data")
    def test_icd11_id_with_prefix(self):
        q = 'CA01.001'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(
            q.split(":")[1], res, 'mondo.xrefs.icd11', True)

    # HP IDs
    def test_hp_id_with_prefix(self):
        q = 'HP:0001250'
        res = self.request("disease", method="POST", data={"ids": q})
        res = res.json()
        assert len(res) == 1
        assert self.value_in_result(q, res, 'disgenet.xrefs.hp', True)

    # ignore_obsolete parameter
    def test_ignore_obsolete_true(self):
        q = 'MONDO:0000006'
        res = self.request("query", method="POST",
                           data={"q": q, "ignore_obsolete": True})
        res = res.json()
        assert len(res) == 1
        assert res[0]['notfound'] is True

    def test_ignore_obsolete_false(self):
        q = 'MONDO:0000006'
        res = self.request("query", method="POST",
                           data={"q": q, "ignore_obsolete": False})
        res = res.json()
        assert len(res) == 1
        assert res[0]['_id'] == q
