from typing import Any, Union

import pandas as pd
from pandas import DataFrame

chebi_name_df = None
is_a_df = None

ec_df = None
ecocyc_df = None

def make_curie(local_id:Any, prefix:str) -> str:
    """
    Ensures that a given local_id is in curie format:
    "{prefix}:{local_id}"
    """
    if not isinstance(local_id, str):
        local_id = str(local_id)

    if ':' not in local_id:
        local_id = '{}:{}'.format(prefix, local_id)

    return local_id.upper()

def make_local_rhea_id(identifier:str) -> str:
    if ':' in identifier:
        _, identifier = identifier.split(':', 1)
    return identifier

def make_dataframe(path:str, index, header='infer', names=None) -> DataFrame:
    df = pd.read_csv(path, sep='\t', header=header, names=names, dtype=str)
    return df.set_index(index)

def rhea2ecocyc(rhea_id:str) -> str:
    global ecocyc_df

    if ecocyc_df == None:
        ecocyc_df = make_dataframe(path='rhea/rhea2ecocyc.tsv', index='RHEA_ID')

    rhea_id = make_local_rhea_id(rhea_id)

    return ecocyc_df.loc[rhea_id].at['ID']

def rhea2ec(rhea_id:Union[str, int]) -> str:
    global ec_df

    if ec_df == None:
        ec_df = make_dataframe(path='rhea/rhea2ec.tsv', index='RHEA_ID')

    rhea_id = make_local_rhea_id(rhea_id)

    return ec_df.loc[rhea_id].at['ID']

def is_a(rhea_id:Union[str, int]) -> str:
    global is_a_df

    if is_a_df == None:
        is_a_df = make_dataframe(path='rhea/rhea-relationships.tsv', index='FROM_REACTION_ID')

    rhea_id = make_local_rhea_id(rhea_id)

    return str(is_a_df.loc[rhea_id].at['TO_REACTION_ID'])

def chebi2name(chebiId:str) -> str:
    global chebi_name_df

    if chebi_name_df == None:
        chebi_name_df = make_dataframe(
            path='rhea/chebiId_name.tsv',
            index='chebiId',
            header=None,
            names=['chebiId', 'name']
        )

    chebiId = make_curie(chebiId, 'CHEBI')

    return chebi_name_df.loc[chebiId].at['name'].strip()



if __name__ == '__main__':
    assert(chebi2name('CHEBI:368997') == 'N-benzyloxycarbonylglycine')
    assert(is_a('53555') == '53563')
    assert(rhea2ec('10528') == '1.14.14.100')
    assert(rhea2ecocyc('10489') == '5-FORMYL-THF-CYCLO-LIGASE-RXN')
    print('All passed')
