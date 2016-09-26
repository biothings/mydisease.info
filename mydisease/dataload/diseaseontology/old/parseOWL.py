
# don't use this

import json
from pprint import pprint

import requests
from rdflib import Graph

url = "http://www.berkeleybop.org/ontologies/doid.owl"
r = requests.get(url)

g = Graph().parse(data=r.text, format='application/rdf+xml')

d = g.serialize(format='json-ld', indent=4)
dd=json.loads(d.decode('utf-8'))


oboid = 'http://www.geneontology.org/formats/oboInOwl#id'
ddd = {x[oboid][0]['@value']: x for x in dd if oboid in x}
pprint(ddd['DOID:12096'])