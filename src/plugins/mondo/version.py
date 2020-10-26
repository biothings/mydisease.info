def get_release(self):
    import requests

    doc = requests.get("http://purl.obolibrary.org/obo/mondo.obo")
    for line in doc.iter_lines():
        line = line.decode("utf-8")
        if line.startswith("#date:"):
            version = line.split(":")[-1].strip()
            return version