from swagger_server.models.beacon_predicate import BeaconPredicate

from cachetools.func import ttl_cache

from controller_impl import utils

__time_to_live_in_seconds = 604800

@ttl_cache(maxsize=500, ttl=__time_to_live_in_seconds)
def get_predicates():
	"""get_predicates

	Get a list of predicates used in statements issued by the knowledge source  # noqa: E501


	:rtype: List[Predicate]
	"""

	return "predicates"
