import requests

from swagger_server.models.beacon_knowledge_map_statement import BeaconKnowledgeMapStatement
from swagger_server.models.beacon_knowledge_map_object import BeaconKnowledgeMapObject
from swagger_server.models.beacon_knowledge_map_subject import BeaconKnowledgeMapSubject
from swagger_server.models.beacon_knowledge_map_predicate import BeaconKnowledgeMapPredicate

from swagger_server.models.beacon_concept_category import BeaconConceptCategory

from cachetools.func import ttl_cache
from controller_impl import utils

_MONARCH_PREFIX_URI='https://api.monarchinitiative.org/api/identifier/prefixes/'

__time_to_live_in_seconds = 604800

@ttl_cache(maxsize=300, ttl=__time_to_live_in_seconds)
def get_concept_categories():  # noqa: E501
	"""get_concept_types

	Get a list of types and # of instances in the knowledge source, and a link to the API call for the list of equivalent terminology  # noqa: E501


	:rtype: List[BeaconConceptType]
	"""

	return "concept categories"

@ttl_cache(maxsize=300, ttl=__time_to_live_in_seconds)
def get_knowledge_map():
	"""get_knowledge_map

	Get a high level knowledge map of the all the beacons by subject semantic type, predicate and semantic object type  # noqa: E501


	:rtype: List[KnowledgeMapStatement]
	"""

	return "knowledge map"
