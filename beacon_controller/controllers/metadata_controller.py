from swagger_server.models.beacon_concept_category import BeaconConceptCategory  # noqa: E501
from swagger_server.models.beacon_knowledge_map_statement import BeaconKnowledgeMapStatement  # noqa: E501
from swagger_server.models.beacon_knowledge_map_object import BeaconKnowledgeMapObject
from swagger_server.models.beacon_knowledge_map_subject import BeaconKnowledgeMapSubject
from swagger_server.models.beacon_knowledge_map_predicate import BeaconKnowledgeMapPredicate
from swagger_server.models.beacon_predicate import BeaconPredicate  # noqa: E501
from swagger_server.models.namespace import Namespace
from swagger_server.models.local_namespace import LocalNamespace

from beacon_controller.const import Category, Predicate
from beacon_controller.providers import rhea
from beacon_controller.providers.xrefs import load_df

import beacon_controller.biolink_model as blm
from beacon_controller.providers.xrefs import load_df

import functools

@functools.lru_cache()
def get_namespaces():
    """get_namespaces
    Get a list of namespace (curie prefixes) mappings that this beacon can perform with its /exactmatches endpoint  # noqa: E501
    :rtype: List[LocalNamespace]
    """
    frequency = load_df().RHEA_ID.nunique()

    namespaces = [
        Namespace("KEGG.REACTION", uri='http://identifiers.org/kegg/'),
        Namespace("KEGG", uri='http://identifiers.org/kegg.reaction/'),
        Namespace("METACYC", uri='http://identifiers.org/biocyc/METACYC:'),
        Namespace("ECOCYC", uri='http://identifiers.org/biocyc/ECOCYC:'),
        Namespace("REACTOME", uri='http://identifiers.org/reactome/'),
        Namespace("MACIE", uri='http://identifiers.org/macie/'),
        Namespace("RHEA", uri='http://identifiers.org/rhea/'),
    ]

    return [LocalNamespace(
        local_prefix='RHEA',
        uri='http://identifiers.org/rhea/',
        clique_mappings=namespaces,
        frequency=frequency,
    )]

@functools.lru_cache()
def get_concept_categories():  # noqa: E501
    """get_concept_categories

    Get a list of concept categories and number of their concept instances documented by the knowledge source. These types should be mapped onto the Translator-endorsed Biolink Model concept type classes with local types, explicitly added as mappings to the Biolink Model YAML file. A frequency of -1 indicates the category can exist, but the count is unknown.  # noqa: E501


    :rtype: List[BeaconConceptCategory]
    """
    q="""
    PREFIX rh:<http://rdf.rhea-db.org/>
    SELECT
    (count(distinct ?reaction) as ?reactionCount)
    (count(distinct ?participant) as ?participantCount)
    (count(distinct ?compound) as ?compoundCount)
    (count(distinct ?enzyme) as ?enzymeCount)
    WHERE {
      ?reaction rdfs:subClassOf rh:Reaction .
      ?reaction rh:status rh:Approved .
      OPTIONAL { ?reaction rh:ec ?enzyme . }

      ?reaction rh:side ?reactionSide .
      ?reactionSide rh:contains ?participant .
      ?participant rh:compound ?compound .
    }
    """
    d = rhea.get_records(q)[0]

    compoundCount = d['compoundCount']['value']
    enzymeCount = d['enzymeCount']['value']
    reactionCount = d['reactionCount']['value']

    categories = []
    for category in Category:
        description = blm.get_class(category.name).description
        if category is Category.molecular_activity:
            frequency = reactionCount
        elif category is Category.protein:
            frequency = enzymeCount
        elif category is Category.chemical_substance:
            frequency = compoundCount

        categories.append(BeaconConceptCategory(
            category=category.name,
            local_category=category.name,
            description=description,
            frequency=int(frequency)
        ))

    return categories

@functools.lru_cache()
def get_knowledge_map():  # noqa: E501
    """get_knowledge_map

    Get a high level knowledge map of the all the beacons by subject semantic type, predicate and semantic object type  # noqa: E501


    :rtype: List[BeaconKnowledgeMapStatement]
    """
    kmaps = []
    for predicate in Predicate:
        kmaps.append(BeaconKnowledgeMapStatement(
            description=f'{predicate.domain.name} {predicate.relation.replace("_", " ")} {predicate.codomain.name}',
            subject=BeaconKnowledgeMapSubject(
                category=predicate.domain.name,
                prefixes=predicate.domain.prefixes
            ),
            predicate=BeaconKnowledgeMapPredicate(
                edge_label=predicate.edge_label,
                relation=predicate.relation,
                negated=False
            ),
            object=BeaconKnowledgeMapObject(
                category=predicate.codomain.name,
                prefixes=predicate.codomain.prefixes
            ),
            frequency=get_predicate_count(predicate)
        ))

    return kmaps

@functools.lru_cache()
def get_predicates():  # noqa: E501
    """get_predicates

    Get a list of predicates used in statements issued by the knowledge source  # noqa: E501


    :rtype: List[BeaconPredicate]
    """
    predicates = []
    for predicate in Predicate:
        description = blm.get_slot(predicate.edge_label).description
        predicates.append(BeaconPredicate(
            edge_label=predicate.edge_label,
            relation=predicate.relation,
            frequency=get_predicate_count(predicate),
            description=description
        ))
    return predicates

@functools.lru_cache()
def get_predicate_count(predicate:Predicate):
        q=f"""
        PREFIX rh:<http://rdf.rhea-db.org/>
        SELECT
        (count(distinct ?subjectId) as ?statementCount)
        WHERE {{
            {predicate.sparql}
        }}
        """
        results = rhea.get_records(q)
        for result in results:
            return int(result['statementCount']['value'])
