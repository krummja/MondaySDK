from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()


QUERIES = os.environ["QUERY_PATH"]
MUTATIONS = os.environ["MUTATION_PATH"]


def load_query(query_name: str) -> str:
    """
    Load a GraphQL query from the queries directory.

    The queries directory is specified by the QUERY_PATH environment variable.
    """
    path = Path(QUERIES, query_name + ".graphql")
    with open(path) as f:
        return f.read()


def load_mutation(mutation_name: str) -> str:
    """
    Load a GraphQL mutation from the mutations directory.

    The mutations directory is specified by the MUTATION_PATH environment
    variable.
    """
    path = Path(MUTATIONS, mutation_name + ".graphql")
    with open(path) as f:
        return f.read()
