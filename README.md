# arangodb-pythongraph
Run an AQL and get a Python network object in return

## Installation

```
pip install arangodb-pythongraph
```
Duh.

## Graph frameworks
This package is based on [pyintergraph](https://pypi.org/project/pyintergraph/) and thus supports extraction to NetworkX, python-IGraph and Graph-Tools graph objects.
However, these libraries are not defined as requirements for this package and if you want to extract to each of them you are required to install the necessary package accordingly.


# Usage

All queries **must** return path objects.

## Simple extraction

```
from arangodb_pythongraph import execute_to_pygraph

db = ... # ArangoDB connection (use python-arango package)
example_query = '''
  FOR v0 in vertex_collection
    FOR e, v, p IN OUTBOUND v0 edge_collection
      RETURN p
'''
python_graph = execute_to_pygraph(db, query)
nx_graph = python_graph.to_networkx()
gt_graph = python_graph.to_graph_tool()
ig_graph = python_graph.to_igraph()
```

## Exporting the graph
If you want to export the graph (for example to use it with [Gephi](https://gephi.org/)),
you might run into trouble if you have nested or complex attributes in your graph.
To overcome this, use the `cleanup` argument:
```
python_graph = execute_to_pygraph(db, query, cleanup=True)
```

The functionality might be missing some use cases so if you encounter problems while exporting the graph to file,
please open an Issue describing the error you're getting together with a portion of the data you're trying to export.

# Attaching functionality to the AQL object
For a neater use, run `arangodb_pythongraph.register()`

Before:
```
python_graph = execute_to_pythongraph(db, query)
```

After:
```
python_graph = db.aql.execute_to_pythongraph(query)
```

# Development
Contributions are more than welcome :)

Note that the project is managed with [poetry](https://python-poetry.org/),
so make sure you use poetry to update the pypoject file.

## Running tests
To run the tests you must have a running instance of ArangoDB.
If you don't have a connection to an existing DB you can [use docker](https://www.arangodb.com/download-major/docker/) to run it easily.

Once you have a running ArangoDB connection, create a DB named 'test' (or any other name you choose),
and run tests with pytest
```
ARANGODB_PASS=<pass_goes_here> ARANGODB_NAME=test poetry run pytest
```

