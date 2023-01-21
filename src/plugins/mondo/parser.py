from collections import defaultdict
import networkx as nx
import obonet
import os
import re


def get_synonyms(data):
    """
    Format synonyms as dictionary.
    "exact" and "related" synonyms are the keys, and their values are in lists
    """
    if "synonym" not in data:
        return {}

    exact = []
    related = []
    for syn in data["synonym"]:
        if "EXACT" in syn:
            match = re.findall(r"\"(.+?)\"", syn)
            exact = exact + match
        elif "RELATED" in syn:
            match = re.findall(r"\"(.+?)\"", syn)
            related = related + match

    synonyms = {}
    if len(exact) > 0:
        synonyms["exact"] = exact
    if len(related) > 0:
        synonyms["related"] = related

    return synonyms


def load_data(data_folder):
    path = os.path.join(data_folder, "mondo.obo")

    """
    Note that `type(graph)` is `networkx.classes.multidigraph.MultiDiGraph`
    For `MultiDiGraph.nodes` property/method, see https://networkx.org/documentation/stable/reference/classes/generated/networkx.MultiDiGraph.nodes.html.
    For `MultiDiGraph.edges` property/method, see https://networkx.org/documentation/stable/reference/classes/generated/networkx.MultiDiGraph.edges.html.
    
    Also note that for each term `u` in the obo file, `obonet` will:
    1. for any term `v` in the "is-a" section, set a `(u, v)` edge with key "is-a"
    2. for any term `w` in the "relationship" section, set a `(u, w)` edge with the specific relationship as key (E.g. "has_characteristic")
    See https://github.com/dhimmel/obonet/blob/main/obonet/read.py#L48
    
    An edge's key is NOT part of its "data" dictionary. To list all edges in `(start, end, key)` triple format, `MultiDiGraph.edges(keys=True)` should be used.
    (Instead of `MultiDiGraph.edges(data=True)`)
    """
    graph = obonet.read_obo(path)

    """
    We have decided that the "parents", "children", "ancestors", and "descendants" fields should rely on the topological structure solely with the "is_a" edges.
    See https://github.com/biothings/mydisease.info/issues/44.
    
    Note that the edge keys are necessary here for precise removal of edges. 
    See https://networkx.org/documentation/stable/reference/classes/generated/networkx.MultiDiGraph.remove_edge.html
    """
    edges_to_remove = [(u, v, key) for (u, v, key) in graph.edges(keys=True, data=False) if key != "is_a"]
    graph.remove_edges_from(edges_to_remove)  # In-place operation; no return value

    for node_id in graph.nodes(data=False):
        if not node_id.startswith("MONDO:"):
            continue

        rec = graph.nodes[node_id]
        rec["_id"] = node_id
        rec["mondo"] = node_id

        if rec.get("is_a"):
            rec["parents"] = [parent for parent in rec.pop("is_a") if parent.startswith("MONDO:")]

        if rec.get("xref"):
            xrefs = defaultdict(set)
            for val in rec.get("xref"):
                if ":" in val:
                    prefix, id = val.split(":", 1)
                    if prefix in ["DOID", "HP", "MP", "OBI", "EFO"]:
                        xrefs[prefix.lower()].add(val)
                    elif prefix in ["https", "http"]:
                        continue
                    else:
                        xrefs[prefix.lower()].add(id)
            for k, v in xrefs.items():
                xrefs[k] = list(v)
            rec.pop("xref")
            rec["xrefs"] = dict(xrefs)

        rec["children"] = [
            child
            for child in graph.predecessors(node_id)
            if child.startswith("MONDO:")
        ]

        rec["ancestors"] = [
            ancestor
            for ancestor in nx.descendants(graph, node_id)
            if ancestor.startswith("MONDO:")
        ]

        rec["descendants"] = [
            descendant
            for descendant in nx.ancestors(graph, node_id)
            if descendant.startswith("MONDO:")
        ]

        rec["synonym"] = get_synonyms(rec)

        if rec.get("def"):
            rec["definition"] = rec.pop("def")
        if rec.get("name"):
            rec["label"] = rec.pop("name")
        if rec.get("created_by"):
            rec.pop("created_by")
        if rec.get("creation_date"):
            rec.pop("creation_date")
        if rec.get("property_value"):
            rec.pop("property_value")

        if rec.get("relationship"):
            rels = {}
            for rel in rec.get("relationship"):
                predicate, val = rel.split(" ")
                prefix = val.split(":")[0]
                if predicate not in rels:
                    rels[predicate] = defaultdict(set)
                if prefix.lower() not in rels[predicate]:
                    rels[predicate][prefix.lower()].add(val)
            for m, n in rels.items():
                for p, q in n.items():
                    n[p] = list(q)
                rels[m] = dict(n)
            rec.update(rels)
            rec.pop("relationship")

        yield {"_id": rec.pop("_id"), "mondo": rec}
