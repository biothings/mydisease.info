def get_release(self):
    import requests

    doc = requests.get(
        "http://purl.obolibrary.org/obo/hp/hpoa/phenotype.hpoa"
    )
    return doc.headers.get("last-modified")