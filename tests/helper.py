from arango.database import StandardDatabase
from arangodb_pythongraph import execute_to_pygraph

MOCK_COLLECTION_PREFIX = "arangodb_pythongraph_test_"
CHARACTER_COLLECTION = MOCK_COLLECTION_PREFIX + "characters"
CHARACTER_EDGE_COLLECTION = MOCK_COLLECTION_PREFIX + "childOf"

FETCH_GRAPH_QUERY = """
WITH @@character_collection, @@character_edge_collection
FOR c IN @@character_collection
    FOR v, e, p IN 0..1 OUTBOUND c @@character_edge_collection
        RETURN p
"""

BIND_VARS = {
        '@character_collection': CHARACTER_COLLECTION,
        '@character_edge_collection': CHARACTER_EDGE_COLLECTION
    }


def create_mock_data(db: StandardDatabase):
    db.create_collection(CHARACTER_COLLECTION)
    db.create_collection(CHARACTER_EDGE_COLLECTION, edge=True)

    node_insertion_query = open("tests/resources/insert_characters.aql").read()
    db.aql.execute(node_insertion_query, bind_vars=BIND_VARS)

    edge_insertion_query = open("tests/resources/insert_relations.aql").read()
    db.aql.execute(edge_insertion_query, bind_vars=BIND_VARS)


def erase_mock_data(db: StandardDatabase):
    try:
        db.delete_collection(CHARACTER_EDGE_COLLECTION)
    except:
        pass
    try:
        db.delete_collection(CHARACTER_COLLECTION)
    except:
        pass


def fetch_mock_python_graph(db: StandardDatabase):
    python_graph = execute_to_pygraph(db, FETCH_GRAPH_QUERY, bind_vars=BIND_VARS)
    return python_graph
