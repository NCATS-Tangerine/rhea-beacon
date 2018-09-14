import connexion
from swagger_server.models.beacon_concept_category import BeaconConceptCategory
from swagger_server.models.beacon_knowledge_map_statement import BeaconKnowledgeMapStatement
from swagger_server.models.beacon_predicate import BeaconPredicate
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime

import controller as ctrl

def get_concept_categories():
    """
    get_concept_categories
    Get a list of concept categories and number of their concept instances documented by the knowledge source. These types should be mapped onto the Translator-endorsed Biolink Model concept type classes with local types, explicitly added as mappings to the Biolink Model YAML file. A frequency of -1 indicates the category can exist, but the count is unknown.

    :rtype: List[BeaconConceptCategory]
    """
    return ctrl.get_concept_categories()


def get_knowledge_map():
    """
    get_knowledge_map
    Get a high level knowledge map of the all the beacons by subject semantic type, predicate and semantic object type

    :rtype: List[BeaconKnowledgeMapStatement]
    """
    return ctrl.get_knowledge_map()


def get_predicates():
    """
    get_predicates
    Get a list of predicates used in statements issued by the knowledge source

    :rtype: List[BeaconPredicate]
    """
    return ctrl.get_predicates()
