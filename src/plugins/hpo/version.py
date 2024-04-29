def get_release(self):
    import datetime

    import requests

    doc = requests.get(
        "http://purl.obolibrary.org/obo/hp/hpoa/phenotype.hpoa"
    )
    last_modified = doc.headers.get("last-modified")
    return datetime.datetime.strptime(
        last_modified, "%a, %d %b %Y %H:%M:%S %Z"
    ).strftime("%Y-%m-%d")
