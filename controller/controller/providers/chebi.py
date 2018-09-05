import os
import numpy as np
import pandas as pd

from typing import List

from controller import data_path

compounds_path = data_path('compounds.tsv.gz')
chebi_path = data_path('chebiId_name.tsv')

compounds_df = None

def load():
    """
    Loads the CHEBI dataframe from compounds.tsv.gz, throwing away rows where
    the CHEBI_ACCESSION identifier isn't contained in chebi.tsv.
    """
    global compounds_df

    compounds_df = pd.read_csv(compounds_path, compression='gzip', sep='\t', dtype=str)
    df = pd.read_csv(chebi_path, sep='\t', dtype=str, header=None, names=['CHEBI_ACCESSION', 'rhea_name'])
    compounds_df = pd.merge(compounds_df, df, how='inner', on='CHEBI_ACCESSION')
    compounds_df = compounds_df.replace({np.nan : None})
    compounds_df = compounds_df.applymap(lambda x: x.strip() if type(x) is str else x)

def search(keywords:List[str]) -> List[dict]:
    if compounds_df is None:
        load()

    df = None
    for keyword in keywords:
        for s in ['NAME', 'DEFINITION', 'rhea_name']:
            if df is None:
                df = compounds_df[s].str.contains(keyword, regex=False)
            else:
                df |= compounds_df[s].str.contains(keyword, regex=False)

    result = compounds_df[df == True]

    if result.shape[0] == 0:
        return []

    f = lambda x: 0 if not isinstance(x, str) else sum(k in x for k in keywords)
    result['search_score'] = result.apply(lambda row: f(row['DEFINITION']) + max(f(row['rhea_name']), f(row['NAME'])), axis=1)

    result = result[['CHEBI_ACCESSION', 'NAME', 'DEFINITION', 'rhea_name', 'search_score']]

    result.sort_values(by=['search_score'], ascending=False, inplace=True)
    result.rename(columns={'CHEBI_ACCESSION' : 'id', 'NAME' : 'chebi_name', 'DEFINITION' : 'definition'}, inplace=True)

    return result.to_dict(orient='records')

def search_single(keyword:str) -> List[dict]:
    """
    Returns a list of dictionaries, each having the keys: id, name, definition.
    """
    if compounds_df is None:
        load()

    df = None
    for s in ['NAME', 'DEFINITION', 'rhea_name']:
        if df is None:
            df = compounds_df[s].str.contains(keyword, regex=False)
        else:
            df |= compounds_df[s].str.contains(keyword, regex=False)

    result = compounds_df[df == True]
    result = result[['CHEBI_ACCESSION', 'NAME', 'DEFINITION', 'rhea_name']]
    result.rename(columns={'CHEBI_ACCESSION' : 'id', 'NAME' : 'chebi_name', 'DEFINITION' : 'definition'}, inplace=True)

    return result.to_dict(orient='records')

def get(chebiId:str) -> dict:
    """
    Takes a chebiId and returns a dictionary representing the first row
    for that identifier. Returns an empty dictionary if no row found.
    """
    if compounds_df is None:
        load()

    chebiId = chebiId.upper()
    results = compounds_df.loc[compounds_df['CHEBI_ACCESSION'] == chebiId].to_dict(orient='records')

    for molecule in results:
        for key, value in molecule.items():
            molecule[key] = value.strip() if value is not None else None
        return molecule
    else:
        return {}


if __name__ == '__main__':
    from pprint import pprint
    pprint(search('caffeine'))
