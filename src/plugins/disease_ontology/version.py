def get_release(self):
    import requests

    doc = requests.get(
        "https://raw.githubusercontent.com/DiseaseOntology/HumanDiseaseOntology/main/src/ontology/doid.obo"
    )
    for line in doc.iter_lines():
        line = line.decode("utf-8")
        if line.startswith("data-version:"):
            version = line.split(":")[-1].split("/")[-2]
            return version
