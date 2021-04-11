from typing import Dict, Iterable

from arango.aql import AQL
from arango.database import StandardDatabase
from pyintergraph import InterGraph

DEFAULT_LABEL = '_id'

VERTICES = 'vertices'
EDGES = 'edges'


def _split_graph_obj_to_vertices_edges(res: Dict):
    vertices = {v[DEFAULT_LABEL]: v for v in res.get(VERTICES, [])}
    edges = {(e['_from'], e['_to']): e for e in res.get(EDGES, [])}
    return vertices, edges


def _attr_cleanup(attrs: dict):
    keys_to_remove = [k for k, v in attrs.items()
                      if v is None
                      or (isinstance(v, list) and len(v) < 1)
                      or (isinstance(v, dict))
                      #                      or k in ['properties', 'source']
                      ]
    for k in keys_to_remove:
        attrs.pop(k)
    #     if 'name' in attrs:
    #         attrs['original_name'] = attrs.pop('name')
    unicode_issues = [k for k, v in attrs.items()
                      if isinstance(v, str)]
    for k in unicode_issues:
        attrs[k] = attrs[k].encode('ascii', 'xmlcharrefreplace').decode()


def graph_cleanup(graph: InterGraph):
    """
    Removes problematic attributes from the graph to allow it to be exported.
    Currently removes nulls, empty lists, and dict, and re-encodes strings to avoid non-ascii chars
    :param graph: InterGraph graph
    :return: Nothing
    """
    for attrs in graph.node_attributes + graph.edge_attributes:
        _attr_cleanup(attrs)


def get_graph_from_path_collection(cur: Iterable, label=DEFAULT_LABEL) -> InterGraph:
    nodes_dict, edges_dict = dict(), dict()

    for res in cur:
        if VERTICES in res:  #
            new_vertices, new_edges = _split_graph_obj_to_vertices_edges(res)
            nodes_dict.update(new_vertices)
            edges_dict.update(new_edges)
        else:
            # Fail if results are not a graph
            # TODO: support documents.
            #   If node documents return an unconnnected graph;
            #   if edge documents create nodes with no attributes based on the edges
            raise ValueError("Results should be paths")

    nodes = list(nodes_dict.keys())
    node_labels = {k: v[label] for k, v in nodes_dict.items()}
    node_attributes = list(nodes_dict.values())

    edges = list(edges_dict.keys())
    edge_attributes = list(edges_dict.values())

    is_directed = True  # It seems that Arango supports only directed graphs

    return InterGraph(nodes, node_labels, node_attributes, edges, edge_attributes, is_directed)


def execute_to_pygraph(db: StandardDatabase, query: str, label: str = DEFAULT_LABEL, cleanup: bool = False, **kwargs):
    """Run a query and return a PythonGraph.

    :param db: ArangoDB connection.
    :type query: arango.database.StandardDatabase
    :param query: Query to execute.
    :type query: str
    :param cleanup: Remove problematic attributes from the graph to allow it to be exported.
    :type cleanup: bool
    :param **kwargs: Additional arguments for db.aql.execute (e.g. bind_vars,
    :type opt_rules: list

    :return: Python graph representation
    :rtype: InterGraph
    :raise ValueError: If the query result is not a graph.
    """
    return _execute_to_pythongraph(db.aql, query, label, cleanup, **kwargs)


def _execute_to_pythongraph(aql: AQL, query: str, label=DEFAULT_LABEL, cleanup: bool = False, **kwargs):
    """Run a query and return a PythonGraph.

    :param aql: AQL instance.
    :type query: arango.database.StandardDatabase
    :param query: Query to execute.
    :type query: str
    :param cleanup: Remove problematic attributes from the graph to allow it to be exported.
    :type cleanup: bool
    :param **kwargs: Additional arguments for db.aql.execute (e.g. bind_vars,
    :type opt_rules: list

    :return: Python graph representation
    :rtype: InterGraph
    :raise ValueError: If the query result is not a graph.
    """
    cur = aql.execute(query, **kwargs)
    graph = get_graph_from_path_collection(cur, label=label)
    if cleanup:
        graph_cleanup(graph)
    return graph


def register():
    """Registers the query to pythongraph function as part of the AQL object.

    Before:
    >> python_graph = execute_to_pythongraph(db, query)

    After:
    >> python_graph = db.aql.execute_to_pythongraph(query)

    """
    AQL.execute_to_pythongraph = _execute_to_pythongraph

