import os
import re
from collections import defaultdict

import networkx as nx
import obonet
from biothings.utils.dataload import dict_sweep


class MondoOntologyHelper:
    IS_A_EDGE_TYPE = "is_a"
    MONDO_PREFIX = "MONDO:"

    SYNONYM_PATTERN = re.compile(r"\"(.+?)\"")

    XREF_INVALID_PREFIXES = {"https", "http"}
    # If a curies starts with one of the following prefixes, its ID component should always be prefixed.
    # E.g. "DOID:0080637" should be split into two components like `{"doid": "DOID:0080637"}` (instead of `{"doid": "0080637"}`)
    # See https://github.com/biothings/biomedical_id_resolver.js/blob/master/src/config.ts#L4
    XREF_ALWAYS_PREFIXED = {"DOID", "HP", "MP", "OBI", "EFO"}

    @classmethod
    def load_obo_network(cls, filepath: str) -> nx.MultiDiGraph:
        """
        Note that `type(graph)` is `networkx.classes.multidigraph.MultiDiGraph`
        For `MultiDiGraph.nodes` property/method, see https://networkx.org/documentation/stable/reference/classes/generated/networkx.MultiDiGraph.nodes.html.
        For `MultiDiGraph.edges` property/method, see https://networkx.org/documentation/stable/reference/classes/generated/networkx.MultiDiGraph.edges.html.

        Also note that for each term `u` in the obo file, `obonet` will:
        1. for any term `v` in the "is-a" section, set a `(u, v)` edge with key "is-a"
        2. for any term `w` in the "relationship" section, set a `(u, w)` edge with the specific relationship as key (E.g. "has_characteristic")
        See https://github.com/dhimmel/obonet/blob/main/obonet/read.py#L48
        """
        graph = obonet.read_obo(filepath, ignore_obsolete=False)

        """
        We have decided that the "parents", "children", "ancestors", and "descendants" fields should rely on the topological structure solely with the "is_a"
        edges. See https://github.com/biothings/mydisease.info/issues/44.

        An edge's key is NOT part of its "data" dictionary. To list all edges in `(start, end, key)` triple format, `MultiDiGraph.edges(keys=True)` should be
        used, instead of `MultiDiGraph.edges(data=True)`.

        Also note that the edge keys are necessary here for precise removal of edges.
        See https://networkx.org/documentation/stable/reference/classes/generated/networkx.MultiDiGraph.remove_edge.html
        """
        edges_to_remove = [(u, v, key) for (u, v, key) in graph.edges(
            keys=True, data=False) if key != cls.IS_A_EDGE_TYPE]
        # In-place operation; no return value
        graph.remove_edges_from(edges_to_remove)

        return graph

    @classmethod
    def parse_synonyms(cls, node_obj: dict) -> dict:
        """
        Format synonyms as dictionary.
        "exact" and "related" synonyms are the keys, and their values are in lists
        """
        if "synonym" not in node_obj:
            return {}

        exact_synonyms = []
        related_synonyms = []
        for synonym_description in node_obj["synonym"]:
            # an example of EXACT synonym_description is '"microphthalmia, isolated" EXACT [OMIMPS:251600]'
            if "EXACT" in synonym_description:
                synonyms = cls.SYNONYM_PATTERN.findall(
                    synonym_description)  # e.g. ['microphthalmia, isolated']
                exact_synonyms = exact_synonyms + synonyms
            # an example of RELATED synonym_description is '"eye and adnexa disease" RELATED [DOID:1492]'
            elif "RELATED" in synonym_description:
                synonyms = cls.SYNONYM_PATTERN.findall(
                    synonym_description)  # e.g. ['eye and adnexa disease']
                related_synonyms = related_synonyms + synonyms

        synonyms = dict()
        if len(exact_synonyms) > 0:
            synonyms["exact"] = exact_synonyms
        if len(related_synonyms) > 0:
            synonyms["related"] = related_synonyms

        return synonyms

    @classmethod
    def parse_xref(cls, node_obj: dict) -> dict:
        if "xref" not in node_obj:
            return {}

        xrefs = defaultdict(set)
        for curie in node_obj.get("xref"):
            # E.g. curie == "DOID:0080637", curie_prefix == "DOID", curie_id == "0080637"
            curie_prefix, curie_id = curie.split(":", 1)

            if curie_prefix in cls.XREF_INVALID_PREFIXES:
                continue

            if curie_prefix in cls.XREF_ALWAYS_PREFIXED:
                xrefs[curie_prefix.lower()].add(curie)
            else:
                xrefs[curie_prefix.lower()].add(curie_id)

        # change the data type of values from `set` to `list`
        for curie_prefix, curie_id_col in xrefs.items():
            xrefs[curie_prefix] = list(curie_id_col)

        return xrefs

    @classmethod
    def parse_relationship(cls, node_obj: dict) -> dict:
        if "relationship" not in node_obj:
            return {}

        rels = dict()
        for relationship_description in node_obj.get("relationship"):
            # E.g. relationship_description == "has_characteristic MONDO:0021128", predicate == "has_characteristic", curie == "MONDO:0021128"
            predicate, curie = relationship_description.split(" ")
            curie_prefix = curie.split(":")[0]
            if predicate not in rels:
                rels[predicate] = defaultdict(set)
            if curie_prefix.lower() not in rels[predicate]:
                rels[predicate][curie_prefix.lower()].add(curie)

        for predicate, curie_dict in rels.items():
            # change the data type of values from `set` to `list`
            for curie_prefix, curie_col in curie_dict.items():
                curie_dict[curie_prefix] = list(curie_col)
            rels[predicate] = dict(curie_dict)

        return rels

    @classmethod
    def is_mondo(cls, node_id: str) -> bool:
        return node_id.startswith(cls.MONDO_PREFIX)

    @classmethod
    def get_ontological_predecessors(cls, graph: nx.MultiDiGraph, node_id: str):
        """
        Get the ontological predecessors (parents) of the `node_id` in the `graph`.

        In a directed graph, for any node `v`,
        - its predecessor is a node `u` such that edge `u->v` exists;
        - its successor is a node `w` such that edge `v->w` exists.

        Note that the topological edge directions in the obo network are reverse to the ontological relationships.
        """
        topological_successors = filter(
            cls.is_mondo, graph.successors(node_id))
        ontological_predecessors = list(topological_successors)
        return ontological_predecessors

    @classmethod
    def get_ontological_successors(cls, graph: nx.MultiDiGraph, node_id: str):
        """
        Get the ontological successors (children) of the `node_id` in the `graph`.

        In a directed graph, for any node `v`,
        - its predecessor is a node `u` such that edge `u->v` exists;
        - its successor is a node `w` such that edge `v->w` exists.

        Note that the topological edge directions in the obo network are reverse to the ontological relationships.
        """
        topological_predecessors = filter(
            cls.is_mondo, graph.predecessors(node_id))
        ontological_successors = list(topological_predecessors)
        return ontological_successors

    @classmethod
    def get_ontological_ancestors(cls, graph: nx.MultiDiGraph, node_id: str):
        """
        Get the ontological ancestors (parents, parents of parents, etc.) of the `node_id` in the `graph`.

        In a directed graph, for any node `v`,
        - its ancestor is a node `u` such that path `u-> ... -> v` exists;
        - its descendant is a node `w` such that path `v-> ... -> w` exists.

        Note that the topological edge directions in the obo network are reverse to the ontological relationships.
        """
        topological_descendants = filter(
            cls.is_mondo, nx.descendants(graph, node_id))
        ontological_ancestors = list(topological_descendants)
        return ontological_ancestors

    @classmethod
    def get_ontological_descendants(cls, graph: nx.MultiDiGraph, node_id: str):
        """
        Get the ontological ancestors (children, children of children, etc.) of the `node_id` in the `graph`.

        In a directed graph, for any node `v`,
        - its ancestor is a node `u` such that path `u-> ... -> v` exists;
        - its descendant is a node `w` such that path `v-> ... -> w` exists.

        Note that the topological edge directions in the obo network are reverse to the ontological relationships.
        """
        topological_ancestors = filter(
            cls.is_mondo, nx.ancestors(graph, node_id))
        ontological_descendants = list(topological_ancestors)
        return ontological_descendants


def load_data(data_folder):
    path = os.path.join(data_folder, "mondo.obo")
    graph = MondoOntologyHelper.load_obo_network(path)

    for node_id in graph.nodes(data=False):
        if not MondoOntologyHelper.is_mondo(node_id):
            continue

        node_doc = dict()

        node_doc["mondo"] = node_id

        node_doc["parents"] = MondoOntologyHelper.get_ontological_predecessors(
            graph, node_id)
        node_doc["children"] = MondoOntologyHelper.get_ontological_successors(
            graph, node_id)
        node_doc["ancestors"] = MondoOntologyHelper.get_ontological_ancestors(
            graph, node_id)
        node_doc["descendants"] = MondoOntologyHelper.get_ontological_descendants(
            graph, node_id)

        node_obj = graph.nodes[node_id]

        # Handling deprecated terms
        if node_obj.get("is_obsolete", "false") == "true":
            node_doc["is_obsolete"] = True
            replaced_by = node_obj.get("replaced_by", None)
            if replaced_by:
                node_doc["replaced_by"] = replaced_by[0]
            node_doc["consider"] = node_obj.get("consider", None)

        node_doc["synonym"] = MondoOntologyHelper.parse_synonyms(node_obj)
        node_doc["xrefs"] = MondoOntologyHelper.parse_xref(node_obj)
        # note that we don't assign the relationship dict to `node_doc["relationship"]`
        node_doc.update(MondoOntologyHelper.parse_relationship(node_obj))

        # The `def` sections in the obo file may contain double quotes, e.g. `"A disease that occurs in animals." [EFO:0005932]`
        node_doc["definition"] = node_obj.get("def", "").replace('"', '')
        node_doc["label"] = node_obj.get("name")

        node_doc = dict_sweep(
            node_doc, vals=[None, [], ""], remove_invalid_list=True)

        doc = {
            "_id": node_id,
            "mondo": node_doc
        }
        yield doc
