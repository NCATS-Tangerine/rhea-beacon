from swagger_server.models.beacon_statement import BeaconStatement

from swagger_server.models.beacon_statement_subject import BeaconStatementSubject
from swagger_server.models.beacon_statement_object import BeaconStatementObject
from swagger_server.models.beacon_statement_predicate import BeaconStatementPredicate

from swagger_server.models.beacon_statement_with_details import BeaconStatementWithDetails
from swagger_server.models.beacon_statement_citation import BeaconStatementCitation
from swagger_server.models.beacon_statement_annotation import BeaconStatementAnnotation

import requests
import xml.etree.ElementTree as etree

from controller_impl import parser as ps
from controller_impl import utils

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
        evidence = get_evidence(e)

    return BeaconStatementWithDetails(
        id=statementId,
        is_defined_by="NCATS Tangerine: Star Informatics",
        provided_by="Rhea",
        qualifiers=[],
        annotation=[],
        evidence=evidence
    )

def get_statements(s, edge_label=None, relation=None, t=None, keywords=None, categories=None, size=None):
    #TODO filter
    #TODO search by non-RHEA reactions
    #TODO fix error response

    statements = []

    for concept_id in s:
        if ps.startswith_rhea(concept_id):
            e = ps.query_concept(concept_id[5:])
            
            beacon_subject = BeaconStatementSubject(
                id=concept_id,
                name=ps.get_name(e),
                categories=ps.RHEA_RXN_CATEGORIES
            )

            #molecules
            molecules = ps.get_molecules(e)
            for molecule in molecules:
                statements.append(createBeaconStatement(
                    beacon_subject=beacon_subject,
                    edge_label='has_participant',
                    relation='',
                    beacon_object=BeaconStatementObject(
                        id=molecule['m_id'],
                        name=molecule['name'],
                        categories=['molecular entity']
                    )
                ))
            
            #reactions
            rxns = ps.get_related_rhea_rxns(e)
            
            for rxn in rxns: 
                statements.append(createBeaconStatement(
                    beacon_subject=beacon_subject,
                    edge_label='overlaps',
                    relation='same participants: ' + rxn['relation'],
                    beacon_object=BeaconStatementObject(
                        id=rxn['r_id'],
                        categories=ps.RHEA_RXN_CATEGORIES
                    )
                ))
            #TODO: add is_a relationship from tsv files
            #TODO: get name for RHEA id
            
            # enzymes
            for e_id in ps.get_ec_ids(e):

                statements.append(createBeaconStatement(
                    beacon_subject=beacon_subject,
                    edge_label='has_participant',
                    relation='IntEnz cross-reference',
                    beacon_object=BeaconStatementObject(
                        id=e_id,
                        categories=['genomic entity']
                    )
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
    

    # statements = []

    # for result in results:
    #     if result['source_is_subject']:
    #         s, o = result['source'], result['target']
    #     else:
    #         o, s = result['source'], result['target']

    #     s_categories = utils.standardize(s['category'])
    #     o_categories = utils.standardize(o['category'])

    #     if result['edge_label'] != None:
    #         edge_label = utils.stringify(result['edge_label'])
    #     else:
    #         edge_label = utils.stringify(result['type'])

    #     beacon_subject = BeaconStatementSubject(
    #         id=s['id'],
    #         name=utils.stringify(s['name']),
    #         categories=utils.standardize(s['category'])
    #     )

    #     beacon_predicate = BeaconStatementPredicate(
    #         edge_label=edge_label,
    #         relation=utils.stringify(result['relation']),
    #         negated=bool(result['negated'])
    #     )

    #     beacon_object = BeaconStatementObject(
    #         id=o['id'],
    #         name=utils.stringify(o['name']),
    #         categories=utils.standardize(o['category'])
    #     )

    #     statement_id = result['statement_id']
    #     if statement_id == None:
    #         statement_id = '{}:{}:{}'.format(s['id'], edge_label, o['id'])

    #     statements.append(BeaconStatement(
    #         id=statement_id,
    #         subject=beacon_subject,
    #         predicate=beacon_predicate,
    #         object=beacon_object
    #     ))

    # return statements
