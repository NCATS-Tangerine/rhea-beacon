import connexion
import six
import requests

from swagger_server.models.beacon_concept import BeaconConcept  # noqa: E501
from swagger_server.models.beacon_concept_with_details import BeaconConceptWithDetails  # noqa: E501
from swagger_server.models.beacon_concept_detail import BeaconConceptDetail
from swagger_server.models.exact_match_response import ExactMatchResponse  # noqa: E501
from swagger_server import util

from typing import List
from collections import defaultdict

from controller.providers import chebi, rhea

import xml.etree.ElementTree as etree

def get_concept_details(conceptId):  # noqa: E501
    """get_concept_details

    Retrieves details for a specified concepts in the system, as specified by a (url-encoded) CURIE identifier of a concept known the given knowledge source.  # noqa: E501

    :param conceptId: (url-encoded) CURIE identifier of concept of interest
    :type conceptId: str

    :rtype: List[BeaconConceptWithDetails]
    """
    if conceptId.startswith('CHEBI:'):
        molecule = chebi.get(conceptId)

        rhea_name = molecule.get('rhea_name')
        chebi_name = molecule.get('chebi_name')

        if rhea_name != chebi_name and chebi_name is not None:
            synonyms = [chebi_name]
        else:
            synonyms = []

        details = []
        for key in ['CREATED_BY', 'MODIFIED_ON', 'PARENT_ID', 'SOURCE', 'STAR', 'STATUS']:
            if key in molecule and molecule[key] is not None:
                details.append(BeaconConceptDetail(
                    tag=key.lower(),
                    value=molecule[key]
                ))

        return [BeaconConceptWithDetails(
            id=molecule['CHEBI_ACCESSION'],
            name=molecule['rhea_name'],
            definition=molecule['DEFINITION'],
            category='chemical substance',
            synonyms=synonyms,
            details=details
        )]

    elif conceptId.startswith('RHEA:'):
        reaction = rhea.get_reaction(conceptId)

        details = [
            BeaconConceptDetail(
                tag='products',
                value=reaction.get('products')
            ),
            BeaconConceptDetail(
                tag='reactants',
                value=reaction.get('reactants')
            )
        ]

        return [BeaconConceptWithDetails(
            id=reaction['reaction_id'],
            name=reaction['reaction_name'],
            category='molecular activity',
            details=details,
            synonyms=[]
        )]
    else:
        logger.warn(f'CURIE {conceptId} does not have a recognized prefix')
        return []

def get_concepts(keywords, categories=None, size=None):
    molecules = []

    molecules = chebi.search(keywords)

    concepts = []

    for molecule in molecules:
        chebi_name = molecule.get('chebi_name')
        rhea_name = molecule.get('rhea_name')

        if chebi_name != rhea_name:
            synonyms = [chebi_name]
        else:
            synonyms = []

        concepts.append(BeaconConcept(
            id=molecule.get('id'),
            name=rhea_name,
            synonyms=synonyms,
            definition=molecule.get('definition')
        ))

    if size is not None:
        concepts = concepts[:size]

    return concepts



def get_exact_matches_to_concept_list(c):  # noqa: E501
    """get_exact_matches_to_concept_list

    Given an input array of [CURIE](https://www.w3.org/TR/curie/) identifiers of known exactly matched concepts [*sensa*-SKOS](http://www.w3.org/2004/02/skos/core#exactMatch), retrieves the list of [CURIE](https://www.w3.org/TR/curie/) identifiers of additional concepts that are deemed by the given knowledge source to be exact matches to one or more of the input concepts **plus** whichever concept identifiers from the input list were specifically matched to  these additional concepts, thus giving the whole known set of equivalent concepts known to this particular knowledge source.  If an empty set is  returned, the it can be assumed that the given knowledge source does  not know of any new equivalent concepts matching the input set. The caller of this endpoint can then decide whether or not to treat  its input identifiers as its own equivalent set.  # noqa: E501

    :param c: an array set of [CURIE-encoded](https://www.w3.org/TR/curie/)  identifiers of concepts thought to be exactly matching concepts, to be used in a search for additional exactly matching concepts [*sensa*-SKOS](http://www.w3.org/2004/02/skos/core#exactMatch).
    :type c: List[str]

    :rtype: List[ExactMatchResponse]
    """
    return []
