from swagger_server.models.beacon_concept import BeaconConcept
from swagger_server.models.beacon_concept_with_details import BeaconConceptWithDetails
from swagger_server.models.exact_match_response import ExactMatchResponse
from swagger_server.models.beacon_concept_detail import BeaconConceptDetail

import yaml
import ast

import requests
import xml.etree.ElementTree as etree

from controller_impl import parser as ps

# RHEA_PREFIX = "RHEA:"
# RHEA_RXN_CATEGORIES = ["molecular activity"]

# #TODO: should maybe be getting this from the document instead of hardcoding it
# BP = "{http://www.biopax.org/release/biopax-level2.owl#}"
# RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"

#TODO: case insensitive

def get_concept_details(conceptId):
    #TODO: find by concepts that are not reactions
    #TODO: include check for 404 not found status code
    if not ps.in_namespace(conceptId):
        return None

    if ps.startswith_rhea(conceptId):
        e = ps.query_concept(conceptId[5:])
        rxn_el = ps.get_rxn_tag(e)
        name = ps.get_name_from_tag(rxn_el)

        details = populate_concept_details(rxn_el)
        
        return BeaconConceptWithDetails(
            id=conceptId,
            name=name,
            categories=ps.RHEA_RXN_CATEGORIES,
            details=details
        )
    elif ps.startswith_ec(conceptId):
        e = ps.query_search(conceptId[3:])
        related_rxns = ps.get_rhea_ids(e)
            
        detail = BeaconConceptDetail(
            tag="related reactions",
            value=", ".join(related_rxns)
        )

        return BeaconConceptWithDetails(
            id=conceptId,
            categories=ps.EC_RXN_CATEGORIES,
            details=[detail]
        )
    else:
        return None

def populate_concept_details(element):
    """
    Populates details with information about qualifiers, and controllers/enzymes, if present
    """
    details = []
    controllers = []
    
    for child in element.iter():
        label = child.tag
        tag = None
        # <bp:COMMENT ...>RHEA:Class of reactions=false</bp:COMMENT>
        if ps.is_comment_tag(label):
            text = child.text.split("=", 2)
            tag = text[0]
            value = text[1]
        # <bp:XREF rdf:resource="#rel/controller/UNIPROT:P12276"/>
        elif ps.is_xref_tag(label):
            controller = ps.get_controller(child)
            if controller is not None:
                controllers.append(controller)
        
        # <bp:EC-NUMBER ...>2.3.1.38</bp:EC-NUMBER>
        elif ps.is_ec_tag(label):
            tag = "Enzyme (EC Number)"
            value = child.text

        if tag is not None:
            detail = BeaconConceptDetail(tag=tag, value=value)
            details.append(detail)

    if controllers:
        detail = BeaconConceptDetail(
            tag="controllers",
            value=", ".join(controllers)
        )

        details.append(detail)

    return details
    
def get_concepts(keywords, categories=None, size=None):
    #TODO: find name info of reaction; also add information from reactants, etc.?
    #TODO: filter by category

    categories = categories if categories is not None else []

    concepts = []
    for keyword in keywords:
        e = ps.query_search(keyword)

        matches = ps.get_rhea_ids(e)

        for rhea_id in matches:
            concept = BeaconConcept(
                id=rhea_id,
                #name=name,
                description=ps.RHEA_WEB_URI + rhea_id,
                categories=ps.RHEA_RXN_CATEGORIES
            )

            concepts.append(concept)
    
    size = size if size is not None and size > 0 else len(concepts)
    
    return concepts[:size]

def get_exact_matches_to_concept_list(c):
    """
    Returns Rhea reactions with same participants, different reactions
    """
    results = []
    # for curie in c:
    #     curie_components = curie.split(":")
    #     namespace = curie_components[0] + ":"
    #     if namespace not in C.NAMESPACES:
    #         results.append(ExactMatchResponse(
    #             id=curie,
    #             within_domain=False,
    #             has_exact_matches=[]
    #         ))
    #     else: 
    #         if curie.startswith(C.EC):
    #             response = requests.get(utils.base_path_search() + curie[3:])
    #         else:
    #             response = requests.get(utils.base_path_search() + curie)
            
    #         utils.check_status(response)

    #         e = etree.fromstring(response.content)

    #         num_results = int(e.find("resultset").attrib["numberofrecordsreturned"])
    #         if num_results > 0:
    #             within_domain = True 
    #             if curie.startswith(C.RHEA):
    #                 has_exact_matches = get_similar_reactions(curie)
    #             else:
    #                 has_exact_matches = []
    #         else: 
    #             within_domain = False
    #             has_exact_matches = [] 
    
    #         results.append(ExactMatchResponse(
    #             id=curie,
    #             within_domain=within_domain,
    #             has_exact_matches=has_exact_matches
    #         ))
    
    return results
    

def get_name(rhea_num):
    """
    Finds name of reaction from RHEA reaction number (e.g. 37175)
    """
    e = ps.query_search(ps.RHEA + rhea_num)

    return ps.get_name(e)


def get_similar_reactions(rhea_curie):
    """
    Finds all reactions with same reactants but different directions
    from given Rhea indentifier (e.g. RHEA:37175)
    """
    matches = []
    # response = requests.get(utils.base_path_reaction() + rhea_curie[5:])

    # e = etree.fromstring(response.content)
    # for reaction in e.iter(C.BP+"relationshipXref"):
    #     if reaction.find(C.BP+"DB-VERSION") is not None:
    #         rxn_id = reaction.findtext(C.BP+"ID")
    #         matches.append(C.RHEA + rxn_id)

    return matches

