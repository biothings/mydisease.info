from collections import defaultdict
from itertools import chain

from pymongo import MongoClient

from . import path

class NDFRT_item:
    def __init__(self, name="", code="", kind="", roles=None, props=None):
        self.name = name
        self.code = code
        self.kind = kind
        self.roles = roles
        self.props = props
        self.drug_used_for_treatment = []

    def __repr__(self):
        return "\n".join([self.name, self.code, self.kind, str(self.roles), str(self.props)])

    def __str__(self):
        return "\n".join([self.name, self.code, self.kind, str(self.roles), str(self.props)])

    def format_drug(self):
        d = {'name': self.props.get('Display_Name', [''])[0],
             'level': self.props.get('Level', [''])[0],
             'fda_unii': self.props.get('FDA_UNII', [''])[0],
             'nui': self.props.get('NUI', [''])[0],
             'rxnorm_cui': self.props.get('RxNorm_CUI', [''])[0],
             'umls_cui': self.props.get('UMLS_CUI', [''])[0]
             }
        return {k: v for k, v in d.items() if v}

    def format_disease(self):
        d = {'name': self.props['Display_Name'][0],
             '_id': 'umls_cui:' + self.props['UMLS_CUI'][0],
             'synonyms': self.props.get('Synonym',[]),
             'xref': {
                'mesh': self.props.get('MeSH_DUI',[]),
                'nui': self.props.get('NUI',[]),
                'rxnorm_cui': self.props.get('RxNorm_CUI',[]),
                'snomedct_us_2016_03_01': self.props.get('SNOMED_CID',[]),
                },
            'drugs_used_for_treatment': self.drug_used_for_treatment
            }
        return d


def parse_xml():
    import xml.etree.ElementTree as et
    from collections import defaultdict
    items = dict()
    kinds = dict()
    tree = et.parse(path)
    root = tree.getroot()
    for conceptdef in root.findall('kindDef'):
        name = conceptdef.find('name').text
        code = conceptdef.find('code').text
        kinds[code] = name
    for conceptdef in root.findall('roleDef'):
        name = conceptdef.find('name').text
        code = conceptdef.find('code').text
        kinds[code] = name
    for conceptdef in root.findall('propertyDef'):
        name = conceptdef.find('name').text
        code = conceptdef.find('code').text
        kinds[code] = name
    for conceptdef in root.findall('conceptDef'):
        name = conceptdef.find('name').text
        code = conceptdef.find('code').text
        kind = conceptdef.find('kind').text
        roles_xml = conceptdef.find('definingRoles').findall("role")
        roles = defaultdict(list)
        for role in roles_xml:
            roles[kinds[role.find("name").text]].append(role.find("value").text)
        properties_xml = conceptdef.find('properties').findall("property")
        props = defaultdict(list)
        for prop in properties_xml:
            props[kinds[prop.find("name").text]].append(prop.find("value").text)

        items[code] = NDFRT_item(name=name, code=code, kind=kind, roles=dict(roles), props=dict(props))
    return items


def _parse():
    items = parse_xml()
    diseases = {k: v for k, v in items.items() if v.kind == 'C16'}
    drugs = {k: v for k, v in items.items() if v.kind == 'C8'}
    for drug in drugs.values():
        drug_treats = drug.roles.get('may_treat {NDFRT}', [])
        for dt in drug_treats:
            diseases[dt].drug_used_for_treatment.append(drug.format_drug())
    return diseases


def parse(mongo_collection=None, drop=True):
    if mongo_collection:
        db = mongo_collection
    else:
        client = MongoClient()
        db = client.mydisease.ndfrt
    if drop:
        db.drop()

    diseases = _parse()
    diseases = {x.format_disease()['_id']: x.format_disease() for x in diseases.values()}

    db.insert_many(diseases.values())
