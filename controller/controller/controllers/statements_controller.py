import connexion
import six
import logging

from swagger_server.models.beacon_statement_object import BeaconStatementObject
from swagger_server.models.beacon_statement_subject import BeaconStatementSubject
from swagger_server.models.beacon_statement import BeaconStatement
from swagger_server.models.beacon_statement_predicate import BeaconStatementPredicate

from swagger_server.models.beacon_statement_with_details import BeaconStatementWithDetails
from swagger_server.models.beacon_statement_annotation import BeaconStatementAnnotation
from swagger_server.models.beacon_statement_citation import BeaconStatementCitation

from swagger_server import util

from controller.providers import chebi, rhea

from collections import defaultdict

logger = logging.getLogger(__file__)

PREDICATE = 'has_participant'
CHEBI_CATEGORY = 'chemical substance'
RHEA_CATEGORY = 'molecular activity'

def get_statement_details(statementId, keywords=None, size=None):
    """
    get_statement_details
    Retrieves a details relating to a specified concept-relationship statement include &#39;is_defined_by and &#39;provided_by&#39; provenance; extended edge properties exported as tag &#x3D; value; and any associated annotations (publications, etc.)  cited as evidence for the given statement.
    :param statementId: (url-encoded) CURIE identifier of the concept-relationship statement (\&quot;assertion\&quot;, \&quot;claim\&quot;) for which associated evidence is sought
    :type statementId: str
    :param keywords: an array of keywords or substrings against which to  filter annotation names (e.g. publication titles).
    :type keywords: List[str]
    :param size: maximum number of concept entries requested by the client; if this argument is omitted, then the query is expected to returned all  the available data for the query
    :type size: int

    :rtype: BeaconStatementWithDetails
    """
    if statementId.count(':') != 4:
        logger.warn('Could not parse statementId: {statementId}')
        return []

    rhea_prefix, rhea_id, predicate, chebi_prefix, chebi_id  = statementId.split(':')

    publications = rhea.get_publications(rhea_id)

    evidences = []

    for publication in publications:
        if 'title' in publication:
            if 'source' in publication:
                label = f'{publication["title"]}, {publication["source"]}'
            else:
                label = publication['title']
        else:
            lable = None

        url = None
        identifier = None
        if 'id' in publication:
            if 'db' in publication:
                identifier = f'{publication["db"]}:{publication["id"]}'
                if publication['db'].lower() == 'pmid':
                    url = f'https://www.ncbi.nlm.nih.gov/pubmed/{publication["id"]}'
            else:
                identifier = publication['id']

        evidences.append(BeaconStatementCitation(
            id=identifier,
            uri=url,
            name=label,
            date=publication.get('year'),
            evidence_type=None
        ))

    if size is not None:
        evidences = evidences[:size]

    if keywords is not None:
        evidences = [a for a in evidences if any(k in a.label for k in keywords)]

    return BeaconStatementWithDetails(
        id=statementId,
        is_defined_by='http://starinformatics.com',
        provided_by='https://www.rhea-db.org/',
        qualifiers=[],
        annotation=[],
        evidence=evidences
    )

def get_statements(s, edge_label=None, relation=None, t=None, keywords=None, categories=None, size=None):
    """get_statements

    Given a specified set of [CURIE-encoded](https://www.w3.org/TR/curie/)  &#39;source&#39; (&#39;s&#39;) concept identifiers,  retrieves a paged list of relationship statements where either the subject or object concept matches any of the input &#39;source&#39; concepts provided.  Optionally, a set of &#39;target&#39; (&#39;t&#39;) concept  identifiers may also be given, in which case a member of the &#39;target&#39; identifier set should match the concept opposing the &#39;source&#39; in the  statement, that is, if the&#39;source&#39; matches a subject, then the  &#39;target&#39; should match the object of a given statement (or vice versa).  # noqa: E501

    :param s: an array set of [CURIE-encoded](https://www.w3.org/TR/curie/) identifiers of  &#39;source&#39; concepts possibly known to the beacon. Unknown CURIES should simply be ignored (silent match failure).
    :type s: List[str]
    :param relations: an array set of strings of Biolink predicate relation name labels against which to constrain the search for statement relations associated with the given query seed concept. The predicate  relation names for this parameter should be as published by  the beacon-aggregator by the /predicates API endpoint as taken from the minimal predicate list of the Biolink Model  (see [Biolink Model](https://biolink.github.io/biolink-model)  for the full list of predicates).
    :type relations: List[str]
    :param t: (optional) an array set of [CURIE-encoded](https://www.w3.org/TR/curie/) identifiers of &#39;target&#39; concepts possibly known to the beacon.  Unknown CURIEs should simply be ignored (silent match failure).
    :type t: List[str]
    :param keywords: an array of keywords or substrings against which to filter concept names and synonyms
    :type keywords: List[str]
    :param categories: an array set of concept categories (specified as Biolink name labels codes gene, pathway, etc.) to which to constrain concepts matched by the main keyword search (see [Biolink Model](https://biolink.github.io/biolink-model) for the full list of codes)
    :type categories: List[str]
    :param size: maximum number of statement entries requested by the query (default 100)
    :type size: int

    :rtype: List[BeaconStatement]
    """
    if edge_label is not None and edge_label != PREDICATE:
        return []
    if categories is not None and CHEBI_CATEGORY not in categories:
        return []

    reaction_map = defaultdict(lambda: defaultdict(list))

    for concept_id in s:
        concept_id = concept_id.upper()
        if concept_id.startswith('CHEBI:'):
            for reaction_id in rhea.find_reactions(concept_id):
                reaction_map[concept_id][reaction_id].append(rhea.get_name(reaction_id))
        elif concept_id.startswith('RHEA:'):
            reaction = rhea.get_reaction(concept_id)
            for substance in reaction['products'] + reaction['reactants']:
                reaction_map[substance.get('id')][concept_id].append(reaction.get('reaction_name'))
        else:
            continue

    statements = []

    for chebi_id, reaction_m in reaction_map.items():
        for reaction_id, reaction_names in reaction_m.items():
            for reaction_name in reaction_names:
                compound_name = chebi.get(chebi_id).get('rhea_name')

                if not reaction_id.startswith('RHEA:'):
                    reaction_id = f'RHEA:{reaction_id}'

                s = BeaconStatementSubject(id=reaction_id, name=reaction_name, categories=[RHEA_CATEGORY])
                o = BeaconStatementObject(id=chebi_id, name=compound_name, categories=[CHEBI_CATEGORY])
                p = BeaconStatementPredicate(edge_label=PREDICATE)
                statement_id = f'{reaction_id}:{PREDICATE}:{chebi_id}'
                statement = BeaconStatement(id=statement_id, subject=s, predicate=p, object=o)
                statements.append(statement)

    if size is not None:
        statements = statements[:size]

    if t is not None:
        statements = [s for s in statements if any(s.object.id.lower() == i.lower() for i in t)]
    if keywords is not None:
        statements = [s for s in statements if any(k.lower() in s.object.name.lower() for k in keywords)]

    return statements
