import requests, os
import xml.etree.ElementTree as etree
import pandas as pd

from typing import List
import logging

from controller import data_path

logger = logging.getLogger(__file__)

rhea2name_path = data_path('rhea2name.tsv')

rhea_name_df = None

def get_name(rhea_id:str) -> str:
    global rhea_name_df

    if rhea_name_df is None:
        rhea_name_df = pd.read_csv(rhea2name_path, sep='\t', dtype=str)
        rhea_name_df = rhea_name_df.set_index('RHEA_ID')

    if ':' not in rhea_id:
        rhea_id = f'RHEA:{rhea_id}'

    try:
        return rhea_name_df.loc[rhea_id].at['Name']
    except KeyError:
        return None

def find_reactions(keyword:str) -> List[str]:
    uri = f'https://www.rhea-db.org/rest/1.0/ws/reaction?q={keyword}'
    response = requests.get(uri)
    if response.ok:
        r = etree.fromstring(response.content)
        ids = [e.text for e in r.iterfind('./resultset/rheaReaction/rheaid/id')]
        return ids
    else:
        logger.warn(f'Could not connect to {uri}')
        return []

def get_reaction(rheaid:str) -> dict:
    if 'RHEA:' in rheaid:
        rheaid = rheaid.replace('RHEA:', '')

    uri = f'https://www.rhea-db.org/rest/1.0/ws/reaction/cmlreact/{rheaid}'
    response = requests.get(uri)

    x = '{http://www.xml-cml.org/schema/cml2/react}'
    if response.ok:
        root = etree.fromstring(response.content)
    else:
        logger.warn(f'Could not connect to {uri}')
        return {}

    rxn = [e.text for e in root.iterfind(f'{x}name') if e.text is not None][0]
    rxn_id = [e.get('value') for e in root.iterfind(f'{x}identifier')][0]


    product_names = [e.text for e in root.iterfind(f'{x}productList/{x}product/{x}molecule/{x}name')]
    product_ids = [e.get('value') for e in root.iterfind(f'{x}productList/{x}product/{x}molecule/{x}identifier')]
    product_formulas = [e.get('formula') for e in root.iterfind(f'{x}productList/{x}product/{x}molecule')]

    reactant_names = [e.text for e in root.iterfind(f'{x}reactantList/{x}reactant/{x}molecule/{x}name')]
    reactant_ids = [e.get('value') for e in root.iterfind(f'{x}reactantList/{x}reactant/{x}molecule/{x}identifier')]
    reactant_formulas = [e.get('formula') for e in root.iterfind(f'{x}reactantList/{x}reactant/{x}molecule')]

    products = []
    for name, chebi, formula in zip(product_names, product_ids, product_formulas):
         products.append({'name' : name, 'id' : chebi, 'formula' : formula})

    reactants = []
    for name, chebi, formula in zip(reactant_names, reactant_ids, reactant_formulas):
        reactants.append({'name' : name, 'id' : chebi, 'formula' : formula})

    return {
        'reaction_name' : rxn,
        'reaction_id' : rxn_id,
        'products' : products,
        'reactants' : reactants
    }

def get_publications(rheaid:str) -> dict:
    uri = f'https://www.rhea-db.org/rest/1.0/ws/reaction/biopax2/{rheaid}'

    response = requests.get(uri)

    if response.ok:
        root = etree.fromstring(response.content)
    else:
        logger.warn(f'Could not connect to {uri}')
        return {}

    bp = '{http://www.biopax.org/release/biopax-level2.owl#}'

    publications = []
    for publication in root.iterfind(f'{bp}publicationXref'):
        d = {}
        for e in publication:
            for s in ['year', 'source', 'title', 'id', 'db']:
                if e.tag == f'{bp}{s.upper()}':
                    d[s] = e.text
                    break
        publications.append(d)

    return publications

if __name__ == '__main__':
    from pprint import pprint
    rxn = cmlreact('24604')
    pprint(rxn)
