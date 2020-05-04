import os

import pytest
import arangodb_pythongraph
from arango import ArangoClient
import networkx

from tests import helper

ARANGODB_DBNAME = os.environ.get('ARANGODB_NAME')
ARANGODB_USER = os.environ.get('ARANGODB_USER', 'root')
ARANGODB_PASS = os.environ.get('ARANGODB_PASS')


@pytest.fixture()
def db():
    client = ArangoClient(hosts='http://localhost:8529')
    db = client.db(ARANGODB_DBNAME, username=ARANGODB_USER, password=ARANGODB_PASS)

    print("Writing mock data for test")
    helper.erase_mock_data(db)
    helper.create_mock_data(db)

    yield db

    print("Erasing mock data for test")
    helper.erase_mock_data(db)


@pytest.fixture()
def nx_graph(db):
    python_graph = helper.fetch_mock_python_graph(db)
    nxG: networkx.DiGraph = python_graph.to_networkx()
    return nxG


class TestNetworkXGraph:
    def test_node_count(self, nx_graph):
        assert len(nx_graph.nodes) == 43

    def test_edge_count(self, nx_graph):
        assert len(nx_graph.edges) == 14


def test_register(db):
    arangodb_pythongraph.register()
    assert hasattr(db.aql, 'execute_to_pythongraph')

