from swagger_server.models.beacon_statement import BeaconStatement
from swagger_server.models.beacon_statement_with_details import BeaconStatementWithDetails
from swagger_server.models.beacon_statement_annotation import BeaconStatementAnnotation
from swagger_server.models.beacon_statement_citation import BeaconStatementCitation
from swagger_server.models.beacon_statement_object import BeaconStatementObject
from swagger_server.models.beacon_statement_predicate import BeaconStatementPredicate
from swagger_server.models.beacon_statement_subject import BeaconStatementSubject

from beacon_controller.providers import rhea, pubmed
from beacon_controller.const import Predicate, Category
import beacon_controller.biolink_model as blm

pubmed_client = pubmed.PubMedRetreiver(email='lance@starinformatics.com')

def get_category(curie):
    prefix, _ = curie.upper().split(':', 1)
    for category in Category:
        if prefix in category.prefixes:
            return category.name

def get_statement_details(statement_id, keywords=None, offset=None, size=None):  # noqa: E501
    """get_statement_details

    Retrieves a details relating to a specified concept-relationship statement include &#39;is_defined_by and &#39;provided_by&#39; provenance; extended edge properties exported as tag &#x3D; value; and any associated annotations (publications, etc.)  cited as evidence for the given statement.  # noqa: E501

    :param statement_id: (url-encoded) CURIE identifier of the concept-relationship statement (\&quot;assertion\&quot;, \&quot;claim\&quot;) for which associated evidence is sought
    :type statement_id: str
    :param keywords: an array of keywords or substrings against which to  filter annotation names (e.g. publication titles).
    :type keywords: List[str]
    :param offset: offset (cursor position) to next batch of annotation entries of amount &#39;size&#39; to return.
    :type offset: int
    :param size: maximum number of evidence citation entries requested by the client; if this  argument is omitted, then the query is expected to returned all of the available annotation for this statement
    :type size: int

    :rtype: BeaconStatementWithDetails
    """
    try:
        subject_id, edge_label, relation, object_id = statement_id.split('|')
    except:
        return

    records = get_records(
        s=[subject_id],
        t=[object_id],
        edge_label=edge_label,
        relation=relation,
        size=1,
        get_citations=True
    )

    for d in records:
        citations = get(d, 'citations', 'value').split('|')

        if offset is not None:
            citations = citations[offset:]

        if size is not None:
            citations = citations[:size]

        result = pubmed_client.get(citations)

        evidence = []
        for citation in citations:
            k = citation.replace('http://rdf.ncbi.nlm.nih.gov/pubmed/', '')
            date = result[k]['pubdate']
            name = result[k]['title']
            evidence.append(BeaconStatementCitation(
                id=citation.replace('http://rdf.ncbi.nlm.nih.gov/pubmed/', 'PUBMED:'),
                uri=citation,
                date=date,
                name=name,
                evidence_type='ECO:0000312'
            ))

        return BeaconStatementWithDetails(
            id=statement_id,
            is_defined_by='rhea-db.org',
            provided_by='STAR Informatics',
            qualifiers=[],
            annotation=[],
            evidence=evidence
        )

def lower(s):
    if isinstance(s, list):
        return [lower(i) for i in s]
    elif isinstance(s, str):
        return s.lower()

def get(d:dict, *keys):
    for key in keys:
        if key in d:
            d = d[key]
        else:
            return None
    return d

def get_records(edge_label=None, relation=None, s=None, t=None, s_keywords=None, t_keywords=None, s_categories=None, t_categories=None, size=None, offset=None, get_citations=False):
    unions = []
    for edge in Predicate:
        if edge.matches(edge_label, relation, s_categories, t_categories):
            if get_citations:
                unions.append(edge.sparql_with_citations)
            else:
                unions.append(edge.sparql)

    if len(unions) == 0:
        # In this case nothing can match the given filters
        return []
    else:
        where_block = ' UNION '.join(f'{s}' for s in unions)

    q=f"""
    PREFIX rh:<http://rdf.rhea-db.org/>
    PREFIX EC:<http://purl.uniprot.org/enzyme/>
    SELECT
      ?subjectId
      ?subjectName
      ?objectId
      ?objectName
      ?edge_label
      ?relation
      {'(GROUP_CONCAT(?citation; SEPARATOR="|") AS ?citations)' if get_citations else ''}
    WHERE {{
        {where_block}
        {rhea.build_id_filter('subjectId', s)}
        {rhea.build_id_filter('objectId', t)}
        {rhea.build_substring_filter('subjectName', s_keywords)}
        {rhea.build_substring_filter('objectName', t_keywords)}
    }}
    {build_offset(offset)}
    {build_size(size)}
    """

    print(q)

    return rhea.get_records(q)

def get_statements(s=None, s_keywords=None, s_categories=None, edge_label=None, relation=None, t=None, t_keywords=None, t_categories=None, offset=None, size=None):  # noqa: E501
    """get_statements

    Given a constrained set of some [CURIE-encoded](https://www.w3.org/TR/curie/) &#39;s&#39; (&#39;source&#39;) concept identifiers, categories and/or keywords (to match in the concept name or description), retrieves a list of relationship statements where either the subject or the object concept matches any of the input source concepts provided.  Optionally, a set of some &#39;t&#39; (&#39;target&#39;) concept identifiers, categories and/or keywords (to match in the concept name or description) may also be given, in which case a member of the &#39;t&#39; concept set should matchthe concept opposite an &#39;s&#39; concept in the statement. That is, if the &#39;s&#39; concept matches a subject, then the &#39;t&#39; concept should match the object of a given statement (or vice versa).  # noqa: E501

    :param s: An (optional) array set of [CURIE-encoded](https://www.w3.org/TR/curie/) identifiers of &#39;source&#39; (&#39;start&#39;) concepts possibly known to the beacon. Unknown CURIES should simply be ignored (silent match failure).
    :type s: List[str]
    :param s_keywords: An (optional) array of keywords or substrings against which to filter &#39;source&#39; concept names and synonyms
    :type s_keywords: List[str]
    :param s_categories: An (optional) array set of &#39;source&#39; concept categories (specified as Biolink name labels codes gene, pathway, etc.) to which to constrain concepts matched by the main keyword search (see [Biolink Model](https://biolink.github.io/biolink-model) for the full list of codes)
    :type s_categories: List[str]
    :param edge_label: (Optional) predicate edge label against which to constrain the search for statements (&#39;edges&#39;) associated with the given query seed concept. The predicate edge_names for this parameter should be as published by the /predicates API endpoint and must be taken from the minimal predicate (&#39;slot&#39;) list of the [Biolink Model](https://biolink.github.io/biolink-model).
    :type edge_label: str
    :param relation: (Optional) predicate relation against which to constrain the search for statements (&#39;edges&#39;) associated with the given query seed concept. The predicate relations for this parameter should be as published by the /predicates API endpoint and the preferred format is a CURIE  where one exists, but strings/labels acceptable. This relation may be equivalent to the edge_label (e.g. edge_label: has_phenotype, relation: RO:0002200), or a more specific relation in cases where the source provides more granularity (e.g. edge_label: molecularly_interacts_with, relation: RO:0002447)
    :type relation: str
    :param t: An (optional) array set of [CURIE-encoded](https://www.w3.org/TR/curie/) identifiers of &#39;target&#39; (&#39;opposite&#39; or &#39;end&#39;) concepts possibly known to the beacon. Unknown CURIEs should simply be ignored (silent match failure).
    :type t: List[str]
    :param t_keywords: An (optional) array of keywords or substrings against which to filter &#39;target&#39; concept names and synonyms
    :type t_keywords: List[str]
    :param t_categories: An (optional) array set of &#39;target&#39; concept categories (specified as Biolink name labels codes gene, pathway, etc.) to which to constrain concepts matched by the main keyword search (see [Biolink Model](https://biolink.github.io/biolink-model) for the full list of codes)
    :type t_categories: List[str]
    :param offset: offset (cursor position) to next batch of statements of amount &#39;size&#39; to return.
    :type offset: int
    :param size: maximum number of concept entries requested by the client; if this argument is omitted, then the query is expected to returned all  the available data for the query
    :type size: int

    :rtype: List[BeaconStatement]
    """

    records = get_records(
        s=s,
        t=t,
        edge_label=edge_label,
        relation=relation,
        s_keywords=s_keywords,
        t_keywords=t_keywords,
        s_categories=s_categories,
        t_categories=t_categories,
        size=size,
        offset=offset
    )

    ec_uri = 'http://purl.uniprot.org/enzyme/'

    statements = []

    for d in records:
        subject_id = get(d, 'subjectId', 'value')
        subject_name = get(d, 'subjectName', 'value')
        object_id = get(d, 'objectId', 'value')
        object_name = get(d, 'objectName', 'value')
        edge_label = get(d, 'edge_label', 'value')
        realtion = get(d, 'relation', 'value')

        if subject_id.startswith(ec_uri):
            subject_id = subject_id.replace(ec_uri, 'EC:')
            subject_name = rhea.get_enzyme_name(subject_id)

        if object_id.startswith(ec_uri):
            object_id = object_id.replace(ec_uri, 'EC:')
            object_name = rhea.get_enzyme_name(object_id)

        subject_category = get_category(subject_id)
        object_category = get_category(object_id)

        s = BeaconStatementSubject(
            id=subject_id,
            name=subject_name,
            categories=[subject_category]
        )

        p = BeaconStatementPredicate(
            edge_label=edge_label,
            relation=realtion,
            negated=False
        )

        o = BeaconStatementObject(
            id=object_id,
            name=object_name,
            categories=[object_category]
        )

        statements.append(BeaconStatement(
            id=f'{s.id}|{p.edge_label}|{p.relation}|{o.id}',
            subject=s,
            predicate=p,
            object=o
        ))

    return statements

def build_offset(offset):
    return f'OFFSET {offset}' if isinstance(offset, int) and offset >= 0 else ''

def build_size(size):
    return f'LIMIT {size}' if isinstance(size, int) and size >= 0 else ''
