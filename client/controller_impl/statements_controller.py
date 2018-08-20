from swagger_server.models.beacon_statement import BeaconStatement

from swagger_server.models.beacon_statement_subject import BeaconStatementSubject
from swagger_server.models.beacon_statement_object import BeaconStatementObject
from swagger_server.models.beacon_statement_predicate import BeaconStatementPredicate

from swagger_server.models.beacon_statement_with_details import BeaconStatementWithDetails
from swagger_server.models.beacon_statement_citation import BeaconStatementCitation
from swagger_server.models.beacon_statement_annotation import BeaconStatementAnnotation

import requests
import xml.etree.ElementTree as etree

import rhea as rh
from controller_impl import parser as ps

def get_evidence(e):
    evidence = []
    for pub in ps.get_evidence(e):
        evidence.append(BeaconStatementCitation(
            id="PMID: " + pub["p_id"],
            name=pub["name"],
            date=pub["date"],
            uri=pub["uri"]
        ))
    return evidence

def get_statement_details(statementId, keywords=None, size=None):
    #TODO: keyword filter?
    statement_components = statementId.split(':')

    if len(statement_components) == 5:
        rhea_rxn_num = statement_components[1]
        e = ps.query_concept(rhea_rxn_num)
        if e is None:
            return None
        evidence = get_evidence(e)

        return BeaconStatementWithDetails(
            id=statementId,
            is_defined_by="NCATS Tangerine: Star Informatics",
            provided_by="Rhea",
            qualifiers=[],
            annotation=[],
            evidence=evidence
        )
    else:
        return None

def get_statements(s, edge_label=None, relation=None, t=None, keywords=None, categories=None, size=None):
    #TODO filter

    statements = []

    for concept_id in s:
        if ps.in_namespace(concept_id):
            if ps.startswith_rhea(concept_id):
                e = ps.query_concept(concept_id[5:])
                if e is None:
                    continue
                
                beacon_subject = BeaconStatementSubject(
                    id=concept_id,
                    name=ps.get_name(e),
                    categories=ps.RHEA_RXN_CATEGORIES
                )

                statements.extend(get_molecule_stmts(e, beacon_subject))
                statements.extend(get_rxn_stmts(e, beacon_subject))
                statements.extend(get_ec_stmts(e, beacon_subject))
            else:
                e = ps.query_search(concept_id)
                if e is None:
                    continue
                
                rhea_ids = ps.get_rhea_ids(e)
                name = None
                if ps.startswith_chebi(concept_id) or ps.startswith_generic(concept_id):
                    name = rh.chebi2name(concept_id)
                    categories = ps.CHEBI_RXN_CATEGORIES
                elif ps.startswith_ec(concept_id):
                    categories = ps.EC_RXN_CATEGORIES
                
                beacon_object = BeaconStatementObject(
                    id=concept_id,
                    name=name,
                    categories=categories
                )

                for r_id in rhea_ids:
                    statements.append(createBeaconStatement(
                        beacon_subject=BeaconStatementSubject(
                            id=r_id,
                            name=rh.rhea2name(r_id),
                            categories=ps.RHEA_RXN_CATEGORIES),
                        edge_label=ps.RXN_TO_MOL,
                        relation='reaction to participant',
                        beacon_object=beacon_object
                    ))

    size = size if size is not None and size > 0 else len(statements)
    return statements[:size]

def createBeaconStatement(beacon_subject, edge_label, relation, beacon_object):
    
    predicate = BeaconStatementPredicate(
        edge_label=edge_label,
        relation=relation,
        negated=False
    )
    statement_id = '{}:{}:{}'.format(beacon_subject.id, edge_label, beacon_object.id)
    return BeaconStatement(
        id=statement_id,
        subject=beacon_subject,
        predicate=predicate,
        object=beacon_object
    )
    
def get_molecule_stmts(e, beacon_subject):
    results = []
    molecules = ps.get_molecules(e)
    for molecule in molecules:
        results.append(createBeaconStatement(
            beacon_subject=beacon_subject,
            edge_label=ps.RXN_TO_MOL,
            relation='reaction to participant',
            beacon_object=BeaconStatementObject(
                id=molecule['m_id'],
                name=molecule['name'],
                categories=ps.CHEBI_RXN_CATEGORIES
            )
        ))
    return results

def get_rxn_stmts(e, beacon_subject):
    results = []
    rxns = ps.get_related_rhea_rxns(e) 
    for rxn in rxns: 
        r_id = rxn['r_id']
        results.append(createBeaconStatement(
            beacon_subject=beacon_subject,
            edge_label=ps.RXN_TO_RXN,
            relation='same participants: ' + rxn['relation'],
            beacon_object=BeaconStatementObject(
                id=r_id,
                name=rh.rhea2name(r_id),
                categories=ps.RHEA_RXN_CATEGORIES
            )
        ))
    
    is_a_rxn = rh.is_a(beacon_subject.id)
    if is_a_rxn is not None:
        results.append(createBeaconStatement(
            beacon_subject=beacon_subject,
            edge_label=ps.RXN_TO_RXN,
            relation="is_a",
            beacon_object=BeaconStatementObject(
                id=is_a_rxn,
                name=rh.rhea2name(is_a_rxn),
                categories=ps.RHEA_RXN_CATEGORIES
            )
        ))
    return results

def get_ec_stmts(e, beacon_subject):
    results = []
    for e_id in ps.get_ec_ids(e):
        results.append(createBeaconStatement(
            beacon_subject=beacon_subject,
            edge_label=ps.RXN_TO_MOL,
            relation='IntEnz cross-reference',
            beacon_object=BeaconStatementObject(
                id=e_id,
                categories=ps.EC_RXN_CATEGORIES
            )
        ))
    return results