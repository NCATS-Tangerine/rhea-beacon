from swagger_server.models.beacon_concept import BeaconConcept
from swagger_server.models.beacon_concept_with_details import BeaconConceptWithDetails
from swagger_server.models.exact_match_response import ExactMatchResponse
from swagger_server.models.beacon_concept_detail import BeaconConceptDetail

import yaml
import ast

import requests
import xml.etree.ElementTree as etree
import rhea as rh

from controller_impl import parser as ps

def get_concept_details(conceptId):
    if not ps.in_namespace(conceptId):
        return None

    if ps.startswith_rhea(conceptId):
        e = ps.query_concept(conceptId)
        if e is None:
            return None
        rxn_el = ps.get_rxn_tag(e)
        name = ps.get_name_from_tag(rxn_el)

        details = get_concept_details_rhea_rxn(rxn_el)

        for xref in get_xrefs_alt(conceptId):
            details.append(BeaconConceptDetail(tag="XRef", value=xref))
        reactome = rh.rhea2reactome(conceptId)
        if reactome:
            details.append(BeaconConceptDetail(tag="XRef", value=', '.join(reactome)))
        
        return BeaconConceptWithDetails(
            id=conceptId,
            name=name,
            categories=ps.RHEA_RXN_CATEGORIES,
            details=details
        )
    elif ps.startswith_chebi(conceptId):
        name = rh.chebi2name(conceptId)
        if name is not None:
            return BeaconConceptWithDetails(
                id=conceptId,
                name=name,
                categories=ps.CHEBI_RXN_CATEGORIES,
                details=[]
            )
    elif ps.startswith_ec(conceptId) or ps.startswith_generic(conceptId):
        # TODO: will return results if partial enzyme given (e.g. just EC:1)
        e = ps.query_search(conceptId)
        if e is None:
            return None
        related_rxns = ps.get_rhea_ids(e)
            
        detail = BeaconConceptDetail(
            tag="related reactions",
            value=", ".join(related_rxns)
        )

        if ps.startswith_ec(conceptId):
            categories = ps.EC_RXN_CATEGORIES
        else:
            categories = ps.CHEBI_RXN_CATEGORIES

        return BeaconConceptWithDetails(
            id=conceptId,
            categories=categories,
            details=[detail]
        )
    else:
        return None

def get_concept_details_rhea_rxn(element):
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
            if len(text) == 2:
                tag, value = text
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
    #TODO: filter by category

    categories = categories if categories is not None else []

    concepts = []
    for keyword in keywords:
        e = ps.query_search(keyword)

        matches = ps.get_rhea_ids(e)

        for rhea_id in matches:
            name = rh.rhea2name(rhea_id)
            concept = BeaconConcept(
                id=rhea_id,
                name=name,
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
    for curie in c:
        has_exact_matches=[]
        within_domain=False
        if ps.in_namespace(curie):
            e = ps.query_search(curie)

            if e is not None:
                num_results = ps.get_num_of_results(e)
                if num_results > 0:
                    within_domain = True 
                    if ps.startswith_rhea(curie):
                        has_exact_matches = get_similar_reactions(curie)

        results.append(ExactMatchResponse(
            id=curie,
            within_domain=within_domain,
            has_exact_matches=has_exact_matches
        ))
    
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
    from given Rhea indentifier (e.g. RHEA:37175), and all references to other databases
    """
    matches = []

    e = ps.query_concept(rhea_curie)
    if e is None:
        return []
    else:
        rhea_rxns = ps.get_related_rhea_rxns(e)
        for rhea_rxn in rhea_rxns:
            matches.append(rhea_rxn['r_id'])
        matches.extend(get_xrefs_alt(rhea_curie))

        return matches

def get_xrefs_alt(rhea_curie):
    ecocyc = rh.rhea2ecocyc(rhea_curie)
    metacyc = rh.rhea2metacyc(rhea_curie)
    kegg = rh.rhea2kegg(rhea_curie)
    macie = rh.rhea2macie(rhea_curie)

    matches = []
    for item in [ecocyc, metacyc, kegg, macie]:
        if item is not None:
            matches.append(item)

    return matches


