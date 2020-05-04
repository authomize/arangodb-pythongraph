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

