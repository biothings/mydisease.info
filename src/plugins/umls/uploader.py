import os.path
from .parser import load_data
import biothings.hub.dataload.storage as storage
import biothings.hub.dataload.uploader as uploader


SRC_META = {
        "url": 'https://www.nlm.nih.gov/research/umls/index.html',
        "license_url" : "https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release/license_agreement.html"
        }

class UMLSUploader(uploader.BaseSourceUploader):

    name = "umls"
    storage_class = storage.MergerStorage  # Try to combine duplicate documents.
    __metadata__ = {"src_meta": SRC_META}

    def load_data(self, data_folder):
        umls_docs = load_data(data_folder)
        return umls_docs