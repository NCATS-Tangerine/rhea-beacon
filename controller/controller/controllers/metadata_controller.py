import connexion
import six

from swagger_server.models.beacon_concept_category import BeaconConceptCategory  # noqa: E501
from swagger_server.models.beacon_knowledge_map_statement import BeaconKnowledgeMapStatement  # noqa: E501
from swagger_server.models.beacon_knowledge_map_subject import BeaconKnowledgeMapSubject
from swagger_server.models.beacon_knowledge_map_object import BeaconKnowledgeMapObject
from swagger_server.models.beacon_knowledge_map_predicate import BeaconKnowledgeMapPredicate
from swagger_server.models.beacon_predicate import BeaconPredicate  # noqa: E501
from swagger_server import util


def get_concept_categories():  # noqa: E501
    """get_concept_categories

    Get a list of concept categories and number of their concept instances documented by the knowledge source. These types should be mapped onto the Translator-endorsed Biolink Model concept type classes with local types, explicitly added as mappings to the Biolink Model YAML file.   # noqa: E501


    :rtype: List[BeaconConceptCategory]
    """
    return [
        BeaconConceptCategory(category='chemical substance'),
        BeaconConceptCategory(category='molecular activity'),
    ]


def get_knowledge_map():  # noqa: E501
    """get_knowledge_map

    Get a high level knowledge map of the all the beacons by subject semantic type, predicate and semantic object type  # noqa: E501


    :rtype: List[BeaconKnowledgeMapStatement]
    """
    o = BeaconKnowledgeMapObject(category='chemical substance', prefixes=['CHEBI'])
    s = BeaconKnowledgeMapObject(category='molecular activity', prefixes=['RHEA'])
    p = BeaconKnowledgeMapPredicate(relation='has_participant')
    return [BeaconKnowledgeMapStatement(subject=s, object=o, predicate=p)]

def get_predicates():  # noqa: E501
    """get_predicates

    Get a list of predicates used in statements issued by the knowledge source  # noqa: E501


    :rtype: List[BeaconPredicate]
    """
    return [BeaconPredicate(edge_label='has_participant')]
