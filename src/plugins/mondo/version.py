def get_release(self):
    import requests

    doc = requests.get("http://purl.obolibrary.org/obo/mondo.obo")
    for line in doc.iter_lines():
        line = line.decode("utf-8")
        if line.startswith("data-version:"):
            version = line.split(":")[-1].split("/")[-1]
            return version
