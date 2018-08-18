from swagger_server.models.beacon_concept_category import BeaconConceptCategory
from swagger_server.models.beacon_knowledge_map_statement import BeaconKnowledgeMapStatement
from swagger_server.models.beacon_knowledge_map_subject import BeaconKnowledgeMapSubject
from swagger_server.models.beacon_knowledge_map_predicate import BeaconKnowledgeMapPredicate
from swagger_server.models.beacon_knowledge_map_object import BeaconKnowledgeMapObject
from swagger_server.models.beacon_predicate import BeaconPredicate

from controller_impl import utils
from controller_impl import parser as ps

# Numbers are from https://www.rhea-db.org/statistics
# Up to date as of Aug 16, 2018 - at Rhea release 96
UNIQUE_RHEA_IDS = 11290
SMALL_MOLECULE = 8447
GENERIC_COMPOUND = 1247
POLYMER = 218
NOT_CHEMICAL = 2
INTENZ_EC_NUMBER = 5436 #number of Unique

# compound types are from: https://www.rhea-db.org/documentation #1
LOCAL_CMPD_CAT = "small molecule, generic compound, Rhea polymer"

def pascal_case(s):
    return s.title().replace(' ', '')

def get_concept_categories():
    rhea = ps.RHEA_RXN_CATEGORIES[0]
    chebi = ps.CHEBI_RXN_CATEGORIES[0]
    ec = ps.EC_RXN_CATEGORIES[0]

    rhea_category = BeaconConceptCategory(
        category=rhea,
        description=ps.RHEA_RXN_CAT_DESCR,
        frequency=UNIQUE_RHEA_IDS*4,
        id="biolink:" + pascal_case(rhea),
        local_category="reaction",
        uri="http://bioentity.io/vocab/" + pascal_case(rhea)
    )

    num_cmpds = SMALL_MOLECULE + GENERIC_COMPOUND + POLYMER + NOT_CHEMICAL
    chebi_category = BeaconConceptCategory(
        category=chebi,
        description=ps.CHEBI_RXN_CAT_DESCR,
        frequency=num_cmpds,
        id="biolink:" + pascal_case(chebi),
        local_category=LOCAL_CMPD_CAT,
        uri="http://bioentity.io/vocab/" + pascal_case(chebi)
    )

    ec_category = BeaconConceptCategory(
        category=ec,
        description=ps.EC_RXN_CAT_DESCR,
        frequency=INTENZ_EC_NUMBER,
        id="biolink:" + pascal_case(ec),
        local_category='EC number',
        uri="http://bioentity.io/vocab/" + pascal_case(ec)
    )

    return [rhea_category, chebi_category, ec_category]

def get_knowledge_map():
    
    return []

def get_predicates():
    rxn2rxn_pred = BeaconPredicate(
        edge_label=ps.RXN_TO_RXN,
        description=ps.RXN_TO_RXN_DESCR,
        id="biolink:"+ps.RXN_TO_RXN,
        local_relation="same participants, different direction",
        uri="http://bioentity.io/vocab/" + ps.RXN_TO_RXN,
        frequency = -1
    )

    rxn2mol_pred = BeaconPredicate(
        edge_label=ps.RXN_TO_MOL,
        description=ps.RXN_TO_MOL_DESCR,
        id="biolink:"+ps.RXN_TO_MOL,
        local_relation="participant",
        uri="http://bioentity.io/vocab/" + ps.RXN_TO_MOL,
        frequency = -1
    )

    return [rxn2rxn_pred, rxn2mol_pred]
