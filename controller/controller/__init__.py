import os

def root_dir():
    return os.path.abspath(os.path.dirname(__file__))

def data_path(filename:str) -> str:
    return os.path.join(root_dir(), 'data', filename)

from .controllers.concepts_controller import get_concept_details
from .controllers.concepts_controller import get_concepts
from .controllers.concepts_controller import get_exact_matches_to_concept_list

from .controllers.statements_controller import get_statement_details
from .controllers.statements_controller import get_statements

from .controllers.metadata_controller import get_concept_categories
from .controllers.metadata_controller import get_knowledge_map
from .controllers.metadata_controller import get_predicates
