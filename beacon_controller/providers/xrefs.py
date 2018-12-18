import os

import pandas as pd

from data import path
from typing import List

df = None

def load_df():
    """
    This method loads and returns the dataframe. Rows for EC numbers are dropped
    because these aren't true xrefs.
    """
    global df

    if df is None:
        df = pd.read_csv(os.path.join(path, 'rhea2xrefs.tsv'), sep='\t', dtype=str)
        df = df[df.DB != 'EC']

    return df

def get_xrefs(curie:str) -> List[str]:
    """
    Returns a list of exactly matching CURIE's to the given CURIE. The given
    CURIE is contained in the returned list as long as it's recognized. If
    the returned list is empty then Rhea is not aware of that CURIE.
    """
    if ':' not in curie:
        return []

    curie = curie.upper()
    prefix, local_id = curie.split(':', 1)

    df = load_df()

    if prefix == 'RHEA':
        df = df[(df.RHEA_ID == local_id) | (df.MASTER_ID == local_id)]

        xrefs = set()

        for index, row in df.iterrows():
            if row.DB == 'KEGG_REACTION':
                xrefs.add(f'KEGG:{row.ID}')
                xrefs.add(f'KEGG.REACTION:{row.ID}')

            else:
                xrefs.add(f'{row.DB}:{row.ID}')

            xrefs.add(f'RHEA:{row.RHEA_ID}')
            xrefs.add(f'RHEA:{row.MASTER_ID}')

        return list(xrefs)

    else:
        if prefix == 'KEGG' or prefix == 'KEGG.REACTION':
            df = df[(df.DB == 'KEGG_REACTION') & (df.ID == local_id)]
        else:
            df = df[(df.DB == prefix) & (df.ID == local_id)]

        xrefs = set()

        for index, row in df.iterrows():
            xrefs.update(get_xrefs(f'RHEA:{row.RHEA_ID}'))

            xrefs.add(f'RHEA:{row.RHEA_ID}')
            xrefs.add(f'RHEA:{row.MASTER_ID}')

        return list(xrefs)
