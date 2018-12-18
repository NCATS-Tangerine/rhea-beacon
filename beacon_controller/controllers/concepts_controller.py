from swagger_server.models.beacon_concept import BeaconConcept  # noqa: E501
from swagger_server.models.beacon_concept_with_details import BeaconConceptWithDetails  # noqa: E501
from swagger_server.models.beacon_concept_detail import BeaconConceptDetail
from swagger_server.models.exact_match_response import ExactMatchResponse  # noqa: E501

from beacon_controller import biolink_model as blm
from beacon_controller.providers import rhea
from beacon_controller.providers.xrefs import get_xrefs
from beacon_controller.const import Category, Predicate

def get_concept_details(concept_id):  # noqa: E501
    """get_concept_details

    Retrieves details for a specified concepts in the system, as specified by a (url-encoded) CURIE identifier of a concept known the given knowledge source.  # noqa: E501

    :param concept_id: (url-encoded) CURIE identifier of concept of interest
    :type concept_id: str

    :rtype: BeaconConceptWithDetails
    """
    concept_id = concept_id.upper()

    if concept_id.startswith('EC:'):
        concept = rhea.get_enzyme(concept_id)

        if concept is None:
            return None

        _, ec_number = concept_id.split(':', 1)

        synonyms = concept.get('Synonyms')

        if isinstance(synonyms, str):
            synonyms = synonyms.split(';')
        else:
            synonyms = []

        return BeaconConceptWithDetails(
            id=concept.get('ID'),
            uri=f'https://enzyme.expasy.org/EC/{ec_number}',
            name=concept.get('Name'),
            symbol=None,
            categories=[Category.protein.name],
            description=None,
            synonyms=synonyms,
            exact_matches=[],
            details=[]
        )
    elif concept_id.startswith('RHEA:'):
        records = rhea.get_records(f"""
        PREFIX rh:<http://rdf.rhea-db.org/>
        SELECT
        ?equation
        ?reaction
        WHERE {{
            ?reaction rh:accession "{concept_id}" .
            ?reaction rh:equation ?equation .
        }}
        LIMIT 1
        """)

        for record in records:
            return BeaconConceptWithDetails(
                id=concept_id,
                uri=record['reaction']['value'],
                name=record['equation']['value'],
                symbol=None,
                categories=[Category.molecular_activity.name],
                description=None,
                synonyms=[],
                exact_matches=[],
                details=[]
            )

    else:
        records = rhea.get_records(f"""
        PREFIX rh:<http://rdf.rhea-db.org/>
        SELECT ?compoundAc ?chebi
               (count(distinct ?reaction) as ?reactionCount)
               ?compoundName
        WHERE {{
          ?reaction rdfs:subClassOf rh:Reaction .
          ?reaction rh:status rh:Approved .
          ?reaction rh:side ?reactionSide .
          ?reactionSide rh:contains ?participant .
          ?participant rh:compound ?compound .
          OPTIONAL {{ ?compound rh:chebi ?chebi . }}
          ?compound rh:name ?compoundName .
          ?compound rh:accession "{concept_id}" .
        }}
        LIMIT 1
        """)
        try:
            uri = record['chebi']['value']
        except:
            uri = None

        for record in records:
            return BeaconConceptWithDetails(
                id=concept_id,
                uri=uri,
                name=record['compoundName']['value'],
                symbol=None,
                categories=[Category.chemical_substance.name],
                description=None,
                synonyms=[],
                exact_matches=[],
                details=[BeaconConceptDetail(tag='reactionCount', value=record['reactionCount']['value'])]
            )

def get_concepts(keywords=None, categories=None, offset=None, size=None):  # noqa: E501
    """get_concepts

    Retrieves a list of whose concept in the beacon knowledge base with names and/or synonyms matching a set of keywords or substrings. The results returned should generally be returned in order of the quality of the match, that is, the highest ranked concepts should exactly match the most keywords, in the same order as the keywords were given. Lower quality hits with fewer keyword matches or out-of-order keyword matches, should be returned lower in the list.  # noqa: E501

    :param keywords: (Optional) array of keywords or substrings against which to match concept names and synonyms
    :type keywords: List[str]
    :param categories: (Optional) array set of concept categories - specified as Biolink name labels codes gene, pathway, etc. - to which to constrain concepts matched by the main keyword search (see [Biolink Model](https://biolink.github.io/biolink-model) for the full list of terms)
    :type categories: List[str]
    :param offset: offset (cursor position) to next batch of statements of amount &#39;size&#39; to return.
    :type offset: int
    :param size: maximum number of concept entries requested by the client; if this argument is omitted, then the query is expected to returned all the available data for the query
    :type size: int

    :rtype: List[BeaconConcept]
    """
    concepts = []

    if categories is None or any(a in categories for a in blm.ancestors(Category.protein.name)):
        enzymes, total_num_rows = rhea.find_enzymes(keywords, offset, size, metadata=True)
        for enzyme in enzymes:
            concepts.append(BeaconConcept(
                id=f'EC:{enzyme.get("ID")}',
                name=enzyme.get('Name'),
                categories=[Category.protein.name],
                description=None
            ))

        if size is not None and len(concepts) < size:
            offset = max(0, offset - total_num_rows) if offset is not None else None
            size = size - len(concepts) if size is not None else None
        elif size is None or len(concepts) >= size:
            return concepts

    if categories is None or any(a in categories for a in blm.ancestors(Category.chemical_substance.name)):
        compounds = rhea.find_compounds(keywords, offset=offset, limit=size)
        for compound in compounds:
            concepts.append(BeaconConcept(
                id=compound.get('compoundAc').get('value'),
                name=compound.get('compoundName').get('value'),
                categories=[Category.chemical_substance.name],
                description=None
            ))

    return concepts

def get_exact_matches_to_concept_list(c):  # noqa: E501
    """get_exact_matches_to_concept_list

    Given an input array of [CURIE](https://www.w3.org/TR/curie/) identifiers of known exactly matched concepts [*sensa*-SKOS](http://www.w3.org/2004/02/skos/core#exactMatch), retrieves the list of [CURIE](https://www.w3.org/TR/curie/) identifiers of additional concepts that are deemed by the given knowledge source to be exact matches to one or more of the input concepts **plus** whichever concept identifiers from the input list were specifically matched to these additional concepts, thus giving the whole known set of equivalent concepts known to this particular knowledge source.  If an empty set is returned, the it can be assumed that the given knowledge source does not know of any new equivalent concepts matching the input set. The caller of this endpoint can then decide whether or not to treat  its input identifiers as its own equivalent set.  # noqa: E501

    :param c: an array set of [CURIE-encoded](https://www.w3.org/TR/curie/) identifiers of concepts thought to be exactly matching concepts, to be used in a search for additional exactly matching concepts [*sensa*-SKOS](http://www.w3.org/2004/02/skos/core#exactMatch).
    :type c: List[str]

    :rtype: List[ExactMatchResponse]
    """

    results = []
    for conceptId in c:
        if ':' not in conceptId:
            continue

        xrefs = get_xrefs(conceptId)

        if xrefs != []:
            results.append(ExactMatchResponse(
                id=conceptId,
                within_domain=True,
                has_exact_matches=xrefs
            ))
        else:
            results.append(ExactMatchResponse(
                id=conceptId,
                within_domain=False,
                has_exact_matches=[]
            ))

    return results
