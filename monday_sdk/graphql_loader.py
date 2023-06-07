from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()


QUERIES = os.environ['QUERY_PATH']
MUTATIONS = os.environ['MUTATION_PATH']


def load_query(query_name: str) -> str:
    path = Path(QUERIES, query_name + '.graphql')
    with open(path) as f:
        return f.read()


def load_mutation(mutation_name: str) -> str:
    path = Path(MUTATIONS, mutation_name + '.graphql')
    with open(path) as f:
        return f.read()
