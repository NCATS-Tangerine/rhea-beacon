import requests, string, data, os
import pandas as pd

from beacon_controller.providers.search import search
from collections import defaultdict

import logging

from typing import List

ec_df = None

def load_enzyme_df():
    global ec_df
    if ec_df is None:
        ec_df = pd.read_csv(os.path.join(data.path, 'ecc_names.csv'), sep='\t')
    return ec_df

def get_enzyme(ec_curie):
    ec_curie = ec_curie.lower().replace('ec:', '')
    df = load_enzyme_df()
    df = df.loc[df['ID'] == ec_curie]
    records = df.to_dict(orient='records')
    if len(records) < 1:
        return None
    elif len(records) > 1:
        logging.warn(f'There were multiple records matching {ec_curie} in dataframe')
        return records[0]
    else:
        return records[0]

def get_enzyme_name(ec_curie):
    enzyme = get_enzyme(ec_curie)
    if enzyme is not None:
        return enzyme['Name']
    else:
        return None

def find_enzymes(keywords, offset=None, size=None, metadata=False):
    return search(
        df=load_enzyme_df(),
        columns=['Name', 'Synonyms'],
        keywords=keywords,
        unique_columns='ID',
        offset=offset,
        size=size,
        metadata=metadata
    )

def curies_exist(c:List[str]):
    c = [s.upper() for s in c]

    are_enzymes = [s.startswith('EC:') for s in c]

    select = ' '.join(f'?{i}' for i in range(len(c)))

    opts = []
    for i, (curie, is_enzyme) in enumerate(zip(c, are_enzymes)):
        if is_enzyme:
            opts.append(f'OPTIONAL {{?{i} rh:ec {curie}}} .')
        else:
            opts.append(f'OPTIONAL {{?{i} rh:accession "{curie}"}} .')
    opts = ' '.join(opts)

    q=f"""
    PREFIX rh:<http://rdf.rhea-db.org/>
    PREFIX EC:<http://purl.uniprot.org/enzyme/>
    SELECT {select} WHERE {{
      {opts}
    }}
    """

    results = get(q).get('results').get('bindings')

    if len(results) == 0:
        return [False for s in c]

    d = {}

    for i, curie in enumerate(c):
        if str(i) in results[0]:
            d[curie] = True
        else:
            d[curie] = False

    return d


    # PREFIX rh:<http://rdf.rhea-db.org/>
    # SELECT ?1 ?2 ?3 WHERE {
    #     OPTIONAL { ?1 rh:accession 'CHEBI:29985' } .
    #     OPTIONAL { ?2 rh:accession 'CHEBI:74544' } .
    #     OPTIONAL { ?3 rh:accession 'CHEBI:xyz' } .
    # }

def get(sparql_query):
    response = requests.get(
        url="https://sparql.rhea-db.org/sparql",
        params={
            'query': sparql_query,
            'format' : 'application/sparql-results+json'
        }
    )
    if response.ok:
        return response.json()
    else:
        print(response.text)
        raise Exception(response.text)

def get_records(sparql_query):
    return get(sparql_query).get('results').get('bindings')

def get_all_reactions_that_produce_compound(chebi_curie):
    """
    https://github.com/NCATS-Tangerine/mvp-module-library/blob/master/Rhea/Rhea.py
    """
    return get(
        f"""
        PREFIX rh:<http://rdf.rhea-db.org/>
        PREFIX ec:<http://purl.uniprot.org/enzyme/>
        SELECT ?reaction ?reactionEquation  ?ecNumber ?chebi_id ?curatedOrder WHERE {{
          ?reaction rdfs:subClassOf rh:Reaction;
                    rh:status rh:Approved;
                    rh:ec ?ecNumber;
                    rh:directionalReaction ?directional_reaction.
          ?directional_reaction rh:status rh:Approved;
                                rh:products ?productside;
                                rh:equation ?reactionEquation.
          ?productside rh:curatedOrder ?curatedOrder;
                       rh:contains ?products.
          ?products rh:compound ?small_molecule.
          ?small_molecule rh:accession '{chebi_curie}';
                          rh:accession ?chebi_id.
        }}
        """
    )

def xrefs(rhea_curie):
    """
    8. Select all cross-references (to KEGG, MetaCyc, MACiE, ...) for a given reaction (RHEA:11932)
    """
    rhea_curie = rhea_curie.lower()

    if rhea_curie.startswith('rhea'):
        rhea_curie = rhea_curie.replace('rhea', 'rh')

    return get(
        f"""
        PREFIX rh:<http://rdf.rhea-db.org/>
        SELECT ?reaction ?xref WHERE {{
          ?reaction rdfs:subClassOf rh:Reaction .
          ?reaction rh:directionalReaction ?directionalReaction .
          OPTIONAL {{ ?directionalReaction rdfs:seeAlso ?xref . }}
          ?reaction rh:bidirectionalReaction ?bidirectionalReaction .
          OPTIONAL {{ ?bidirectionalReaction rdfs:seeAlso ?xref . }}
          FILTER (?reaction={rhea_curie})
        }}
        """
    )

def get_rxn_by_pubmed(pubmed_curie):
    """
    6. Select all approved reactions annotated with a given Pubmed ID (2460092)
    """
    pubmed_curie = pubmed_curie.lower()
    if pubmed_curie.startswith('pmid'):
        pubmed_curie = pubmed_curie.replace('pmid', 'pubmed')

    return get(
        f"""
        PREFIX rh:<http://rdf.rhea-db.org/>
        PREFIX pubmed:<http://rdf.ncbi.nlm.nih.gov/pubmed/>
        SELECT ?reaction ?reactionEquation WHERE {{
          ?reaction rdfs:subClassOf rh:Reaction .
          ?reaction rh:status rh:Approved .
          ?reaction rh:equation ?reactionEquation .
          ?reaction rh:citation ?cit .
          filter (?cit={pubmed_curie})
        }}
        """
    )

def get_rxn_by_enzyme(ec_curie):
    return get(
        f"""
        PREFIX rh:<http://rdf.rhea-db.org/>
        PREFIX ec:<http://purl.uniprot.org/enzyme/>
        SELECT ?reaction ?reactionEquation WHERE {{
          ?reaction rdfs:subClassOf rh:Reaction .
          ?reaction rh:status rh:Approved .
          ?reaction rh:equation ?reactionEquation .
          ?reaction rh:ec ?ecNumber
          FILTER (?ecNumber={ec_curie})
        }}
        ORDER BY ?reaction
        """
    )

def escape_regex(s:str) -> str:
    for i in reversed(range(len(s))):
        if s[i] in '\\^$.|?*+()[]\{\}':
            s = f'{s[:i]}\\\\{s[i:]}'
    return s

def build_substring_filter(field:str, keywords:List[str]) -> str:
    if isinstance(keywords, str):
        return build_substring_filter(field, [keywords])
    elif isinstance(keywords, list) and len(keywords) > 0:
        keywords = [escape_regex(k.lower()) for k in keywords]
        disjuncts = [f'regex(lcase(str(?{field})), "{k}")' for k in keywords]
        condition = ' || '.join(disjuncts)
        return f'FILTER ( {condition} ) .'
    else:
        return ''

def build_id_filter(field:str, curies:List[str]) -> str:
    if isinstance(curies, list) and len(curies) > 0:
        disjuncts = []
        for curie in curies:
            curie = curie.upper()
            if curie.startswith('EC'):
                disjuncts.append(f'(?{field} = {curie})')
            else:
                disjuncts.append(f'(?{field} = "{curie}")')
        return f'FILTER ({" || ".join(disjuncts)}) .'

    else:
        return ''

def build_substring_filter2(fields:list, keywords:list) -> str:
    for field in fields:
        keywords = [escape_regex(k.lower()) for k in keywords]
        disjuncts.extend([f'regex(lcase(str(?{field})), "{k}")' for k in keywords])
    condition += ' || '.join(disjuncts)
    return f'FILTER ( {condition} ) .'

def build_limit(limit):
    if isinstance(limit, int):
        return f'LIMIT {limit}'
    else:
        return ''

def build_offset(skip):
    if isinstance(skip, int):
        return f'OFFSET {skip}'
    else:
        return ''

def get_compound(curie):
    curie = curie.upper()
    if curie.startswith('RH:'):
        curie = curie.replace('RH:', 'RHEA:')
    return get(
        f"""
        PREFIX rh:<http://rdf.rhea-db.org/>
        SELECT ?entity ?name ?equation ?xrefs WHERE {{
            ?entity rh:accession '{curie}' .
            OPTIONAL {{ ?entity rh:name ?name }} .
            OPTIONAL {{ ?entity rh:equation ?equation }} .
            OPTIONAL {{ ?entity rdfs:seeAlso ?xrefs }} .
        }}
        """
    )

def find_compounds(keywords, limit=None, offset=None):
    return get_records(
        f"""
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
          ?compound rh:accession ?compoundAc .
          {build_substring_filter('compoundName', keywords)}
        }}
        GROUP BY ?compoundAc ?chebi ?compoundName
        ORDER BY DESC(?reactionCount)
        {build_limit(limit)}
        {build_offset(offset)}
        """
    )

# def find_enzymes(keywords, limit=None, offset=None):
#     """
#     18. Select all approved reactions with CHEBI:17815 (a 1,2-diacyl-sn-glycerol) or one of its descendant. Display the EC numbers if the rhea-ec link exists
#     """
#     return get(
#         f"""
#         PREFIX rh:<http://rdf.rhea-db.org/>
#         PREFIX ch:<http://purl.obolibrary.org/obo/>
#         SELECT distinct ?reaction ?ec ?reactionEquation WHERE {{
#           ?reaction rdfs:subClassOf rh:Reaction .
#           ?reaction rh:status rh:Approved .
#           ?reaction rh:equation ?reactionEquation .
#           ?reaction rh:side ?reactionSide .
#
#           ?reaction rh:ec ?ec .
#
#           ?reactionSide rh:contains ?participant .
#           ?participant rh:compound ?compound .
#           ?compound rh:chebi ?chebi .
#           ?chebi rdfs:subClassOf* ch:CHEBI_17815 .
#         }}
#         order by ?reaction
#         {build_limit(limit)}
#         {build_offset(offset)}
#         """
#     )

def get_rxn_and_compound_by_ec(ec_curie):
    results = get(
        f"""
        PREFIX rh:<http://rdf.rhea-db.org/>
        PREFIX ec:<http://purl.uniprot.org/enzyme/>
        SELECT ?rxnEquation ?rxnID ?side ?compoundName ?compoundID WHERE {{
            ?rxn rh:ec {ec_curie.lower()} .
            ?rxn rh:accession ?rxnID .
            ?rxn rh:equation ?rxnEquation .
            ?rxn rh:side ?side .
            ?side rh:contains ?participant .
            ?participant rh:compound ?compound .
            ?compound rh:accession ?compoundID .
            ?compound rh:name ?compoundName .
        }}
        """
    )
    results = results.get('results').get('bindings')

    rxn_equations = defaultdict(list)
    left_side_ids = defaultdict(list)
    left_side_names = defaultdict(list)
    right_side_ids = defaultdict(list)
    right_side_names = defaultdict(list)

    for d in results:
        rhea = d['rxnID']['value']
        side = d['side']['value']
        rxn_equations[rhea] = d['rxnEquation']['value']
        if side.endswith('_L'):
            left_side_ids[rhea].append(d['compoundID']['value'])
            left_side_names[rhea].append(d['compoundName']['value'])
        elif side.endswith('_R'):
            right_side_ids[rhea].append(d['compoundID']['value'])
            right_side_names[rhea].append(d['compoundName']['value'])
        else:
            raise Exception(f'There should be only left sides or right sides, got: {side}')

    reactions = []
    for rhea_id, equation in rxn_equations.items():
        reactions.append({
            'rhea_id' : rhea_id,
            'equation' : rxn_equations[rhea_id],
            'left_side' : [{'id' : i, 'name' : n} for i, n in zip(left_side_ids[rhea_id], left_side_names[rhea_id])],
            'right_side' : [{'id' : i, 'name' : n} for i, n in zip(right_side_ids[rhea_id], right_side_names[rhea_id])]
        })
    return reactions

def get_ec_and_compound_by_rxn(rhea_curie):
    rhea_curie = rhea_curie.upper().replace('RH:', 'RHEA:')
    results = get(
        f"""
        PREFIX rh:<http://rdf.rhea-db.org/>
        PREFIX ec:<http://purl.uniprot.org/enzyme/>
        SELECT ?rxnEquation ?enzyme ?compoundName ?compoundID WHERE {{
            ?rxn rh:accession "{rhea_curie}" .
            ?rxn rh:equation ?rxnEquation .
            OPTIONAL {{ ?rxn rh:ec ?enzyme }} .
            ?rxn rh:side ?side .
            ?side rh:contains ?participant .
            ?participant rh:compound ?compound .
            ?compound rh:accession ?compoundID .
            ?compound rh:name ?compoundName .
        }}
        """
    )

    enzymes = set()
    equation = None
    compounds = {}
    for result in results.get('results').get('bindings'):
        if 'enzyme' in result:
            enzymes.add(result['enzyme']['value'].replace("http://purl.uniprot.org/enzyme/1.1.1.1", 'EC:'))
        if 'rxnEquation' in result:
            equation = result['rxnEquation']['value']
        if 'compoundID' in result and 'compoundName' in result:
            compounds[results['compoundID']['value']] = result['compoundName']['value']

    return {
        'equation' : equation,
        'enzymes' : [{'id' : e, 'name' : get_enzyme_name(e)} for e in enzymes],
        'compounds' : [{'id' : key, 'name' : value} for key, value in compounds.items()]
    }

def get_all_reactions(curie):
    """
    The given curie may have any of the following prefixes:
    RHEA, EC, CHEBI, POLYMER, GENERAL
    """
    curie = curie.upper()

    if curie.startswith('EC:'):
        select = f'?rxn rh:ec {curie.lower()} .'
    elif curie.startswith('RHEA:') or curie.startswith('RH:'):
        curie = curie.replace('RH:', 'RHEA:')
        select = f'?rxn rh:accession "{curie}" .'
    else:
        select = f'?c rh:accession "{curie}" . ?p rh:compound ?c . ?s rh:contains ?p . ?rxn rh:side ?s .'

    q=f"""
    PREFIX rh:<http://rdf.rhea-db.org/>
    PREFIX ec:<http://purl.uniprot.org/enzyme/>
    SELECT ?enzyme ?rxnEquation ?rxnID ?side ?compoundName ?compoundID WHERE {{
        {select}
        OPTIONAL {{ ?rxn rh:ec ?enzyme }} .
        ?rxn rh:accession ?rxnID .
        ?rxn rh:equation ?rxnEquation .
        ?rxn rh:side ?side .
        ?side rh:contains ?participant .
        ?participant rh:compound ?compound .
        ?compound rh:accession ?compoundID .
        ?compound rh:name ?compoundName .
    }}
    """

    print(q)

    results = get(q)

    results = results.get('results').get('bindings')

    rxn_equations = {}
    enzymes = defaultdict(set)
    left_side_ids = defaultdict(list)
    left_side_names = defaultdict(list)
    right_side_ids = defaultdict(list)
    right_side_names = defaultdict(list)

    for d in results:
        rhea = d['rxnID']['value']
        side = d['side']['value']

        if 'enzyme' in d:
            enzymes[rhea].add(d['enzyme']['value'].replace('http://purl.uniprot.org/enzyme/', 'EC:'))

        rxn_equations[rhea] = d['rxnEquation']['value']
        if side.endswith('_L'):
            left_side_ids[rhea].append(d['compoundID']['value'])
            left_side_names[rhea].append(d['compoundName']['value'])
        elif side.endswith('_R'):
            right_side_ids[rhea].append(d['compoundID']['value'])
            right_side_names[rhea].append(d['compoundName']['value'])
        else:
            raise Exception(f'There should be only left sides or right sides, got: {side}')

    reactions = []
    for rhea_id, equation in rxn_equations.items():
        reactions.append({
            'rhea_id' : rhea_id,
            'equation' : rxn_equations[rhea_id],
            'enzymes' : [{'id' : ec, 'name' : get_enzyme_name(ec)} for ec in enzymes[rhea_id]],
            'left_side' : [{'id' : i, 'name' : n} for i, n in zip(left_side_ids[rhea_id], left_side_names[rhea_id])],
            'right_side' : [{'id' : i, 'name' : n} for i, n in zip(right_side_ids[rhea_id], right_side_names[rhea_id])]
        })
    return reactions


def get_rxn_and_ec_by_compound(curie):
    """
    18. Select all approved reactions with CHEBI:17815 (a 1,2-diacyl-sn-glycerol) or one of its descendant. Display the EC numbers if the rhea-ec link exists
    """
    return get(
        # f"""
        # PREFIX rh:<http://rdf.rhea-db.org/>
        # SELECT distinct ?reaction ?ec ?reactionEquation WHERE {{
        #   ?reaction rdfs:subClassOf rh:Reaction .
        #   ?reaction rh:status rh:Approved .
        #   ?reaction rh:equation ?reactionEquation .
        #   ?reaction rh:side ?reactionSide .
        #
        #   OPTIONAL {{?reaction rh:ec ?ec .}} .
        #
        #   ?reactionSide rh:contains ?participant .
        #   ?participant rh:compound ?compound .
        #   ?compound rh:chebi ?chebi .
        #   ?chebi rdfs:subClassOf* ch:CHEBI_17815 .
        # }}
        # order by ?reaction
        # """
        f"""
        PREFIX rh:<http://rdf.rhea-db.org/>
        SELECT ?rxnID ?rxnEquation ?enzyme ?compoundName WHERE {{
        ?compound rh:accession "{curie.upper()}"
        ?compound rh:name ?compoundName
        ?participant rh:compound ?compound .
        ?side rh:contains ?participant .
        ?rxn rh:side ?side .
        ?rxn rh:accession ?rxnID .
        ?rxn rh:equation ?rxnEquation .
        OPTIONAL {{ ?rxn rh:ec ?enzyme }} .
        """
    )

if __name__ == '__main__':
    from pprint import pprint
    print = pprint
    # print(get_enzyme('1.1.3.13'))
    # print(find_enzymes('Glutathione-dependent formaldehyde'))
    print(find_compounds(['alcoh']))
    # print(escape_regex('n\pd(+)'))
    # pprint(get_all_compounds())
    # pprint(get_rxn_by_enzyme('ec:1.1.1.353'))
    # pprint(get_rxn_by_pubmed())
    # pprint(xrefs('RHEA:11932'))
    # pprint(get_all_reactions_that_produce_compound('CHEBI:48991'))
