from typing import Dict

from arango.aql import AQL
from arango.database import StandardDatabase
from pyintergraph import InterGraph


def _extract_graph_from_graph_response(res: Dict):
    vertices = {v['_id']: v for v in res['vertices']}
    edges = {(e['_from'], e['_to']): e for e in res['edges']}
    return vertices, edges


def execute_to_pygraph(db: StandardDatabase, query: str, label='_id', **kwargs):
    """Run a query and return a PythonGraph.

    :param db: ArangoDB connection.
    :type query: arango.database.StandardDatabase
    :param query: Query to execute.
    :type query: str
    :param **kwargs: Additional arguments for db.aql.execute (e.g. bind_vars,
    :type opt_rules: list

    :return: Python graph representation
    :rtype: InterGraph
    :raise ValueError: If the query result is not a graph.
    """
    return _execute_to_pythongraph(db.aql, query, label, **kwargs)


def _execute_to_pythongraph(aql: AQL, query: str, label='_id', **kwargs):
    """Run a query and return a PythonGraph.

    :param aql: AQL instance.
    :type query: arango.database.StandardDatabase
    :param query: Query to execute.
    :type query: str
    :param **kwargs: Additional arguments for db.aql.execute (e.g. bind_vars,
    :type opt_rules: list

    :return: Python graph representation
    :rtype: InterGraph
    :raise ValueError: If the query result is not a graph.
    """
    cur = aql.execute(query, **kwargs)

    nodes_dict, edges_dict = dict(), dict()

    for res in cur:
        if 'vertices' in res and 'edges' in res:  #
            new_vertices, new_edges = _extract_graph_from_graph_response(res)
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


def register():
    """Registers the query to pythongraph function as part of the AQL object.

    Before:
    >> python_graph = execute_to_pythongraph(db, query)

    After:
    >> python_graph = db.aql.execute_to_pythongraph(query)

    """
    AQL.execute_to_pythongraph = _execute_to_pythongraph

