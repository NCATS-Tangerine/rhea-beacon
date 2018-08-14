from swagger_server.models.beacon_concept import BeaconConcept
from swagger_server.models.beacon_concept_with_details import BeaconConceptWithDetails
from swagger_server.models.exact_match_response import ExactMatchResponse
from swagger_server.models.beacon_concept_detail import BeaconConceptDetail

import yaml
import ast

import requests
import xml.etree.ElementTree as ElementTree

from controller_impl import utils

RHEA_PREFIX = "RHEA:"
RHEA_RXN_CATEGORIES = ["molecular activity"]

#TODO: should maybe be getting this from the document instead of hardcoding it
BP = "{http://www.biopax.org/release/biopax-level2.owl#}"
RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"

def get_concept_details(conceptId):
    #TODO: find by concepts that are not reactions
    #TODO: include check for 404 not found status code
    if conceptId.upper().startswith(RHEA_PREFIX):
        response = requests.get(utils.base_path_reaction() + conceptId[5:])
        utils.check_status(response)

        e = ElementTree.fromstring(response.content)
        rxn_el = e.find(BP + "biochemicalReaction")
        name = rxn_el.findtext(BP + "NAME")

        details = populate_concept_details(rxn_el)
        
        return BeaconConceptWithDetails(
            id=conceptId,
            name=name,
            categories=RHEA_RXN_CATEGORIES,
            details=details
        )
        
    else:
        return None

def populate_concept_details(element):
    """
    Populates details with information about qualifiers, and controllers/enzymes, if present
    """
    details = []
    controllers = []
    CTRL_TAG = "#rel/controller/"

    # for child in element.iter(BP+"COMMENT"):
    #     text = child.text.split("=", 2)
    #     details.append(BeaconConceptWithDetails(tag=text[0], value=text[1]))
    
    # for child in element.iter("./"+BP+"XREF/[rdf:resource])
    
    for child in element.iter():
        label = child.tag
        tag = None
        # <bp:COMMENT ...>RHEA:Class of reactions=false</bp:COMMENT>
        if label == BP + "COMMENT":
            text = child.text.split("=", 2)
            tag = text[0]
            value = text[1]
        # <bp:XREF rdf:resource="#rel/controller/UNIPROT:P12276"/>
        elif label == BP + "XREF":
            text = child.attrib[RDF + "resource"]
            if text.startswith(CTRL_TAG):
                controllers.append(text[len(CTRL_TAG):])
        
        # <bp:EC-NUMBER ...>2.3.1.38</bp:EC-NUMBER>
        elif label == BP + "EC-NUMBER":
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
        response = requests.get(utils.base_path_search() + keyword)
        utils.check_status(response)

        e = ElementTree.fromstring(response.content)

        matches = e.findall("./resultset/rheaReaction/rheaid")

        for match in matches:
            reaction_id = RHEA_PREFIX + match.findtext("id")
            uri = match.find("rheaUri").findtext("uri")

            concept = BeaconConcept(
                id=reaction_id,
                description=uri,
                categories=RHEA_REACTION_CATEGORIES
            )

            concepts.append(concept)
    
    size = size if size is not None and size > 0 else len(concepts)
    
    return concepts[:size]

def get_exact_matches_to_concept_list(c):
    """
    Returns dummy list: Rhea doesn't seem to have much info about exact matches
    """
    results = []
    for curie in c:
        response = requests.get(utils.base_path_search() + curie)
        utils.check_status(response)

        e = ElementTree.fromstring(response.content)

        num_results = e.find("resultset").attrib["numberofrecordsreturned"]
        #TODO: check if this is best way to check equal to 0 in python
        if num_results > 0:
            within_domain = True 
        else: 
            within_domain = False 
        
        results.append(ExactMatchResponse(
            id=curie,
            within_domain=within_domain,
            has_exact_matches=[]
        ))
    
    return results
        

