import json

from biothings.utils.dataload import dict_sweep, unlist

def _map_line_to_json(item):
    # each input JSON doc contains an 'id' field which is in the form of URI
    # need to first check whether the id is 'MONDO'
    if 'id' in item and item['id'].startswith('http://purl.obolibrary.org/obo/MONDO_'):
        mondo_id = item['id'].split('_')[-1]
        # the mondo id should be of length 7
        assert len(mondo_id) == 7
        # convert from URI to curie format of MONDO id
        mondo_id = 'MONDO:' + mondo_id
        # extract disease label
        if 'lbl' in item:
            disease_label = item['lbl']
        else:
            disease_label = None
        # extract disease definition
        if 'meta' in item and 'definition' in item['meta'] and 'val' in item['meta']['definition']:
            disease_definition = item['meta']['definition']['val']
        else:
            disease_definition = None
        # parseing xrefs data
        xref = {}
        if 'meta' in item and 'xrefs' in item['meta']:
            for _xref in item['meta']['xrefs']:
                prefix = _xref['val'].split(':')[0]
                # these ids are naturally displayed as CURIES
                if prefix in ['DOID', 'HP', 'MP', 'OBI']:
                    xref[prefix.lower()] = _xref['val']
                # these are not ids, but are urls
                elif prefix in ['http', 'https']:
                    xref['url'] = _xref['val']
                # the rest of the IDs should only keep the value, not curie
                else:
                    xref[prefix.lower()] = _xref['val'][len(prefix)+1:]
        one_disease_json = {
            "_id": mondo_id,
            "mondo": {
                "label": disease_label,
                "definition": disease_definition,
                "xrefs": xref
            }
        }
        obj = (dict_sweep(unlist(one_disease_json), [None]))
        return obj

def load_data(input_file):
    with open(input_file) as f:
        data = json.loads(f.read())
        mondo_docs = data['graphs'][0]['nodes']
        for record in mondo_docs:
            yield _map_line_to_json(record)