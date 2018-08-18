from typing import Union, List
from rhea.utils import make_curie, make_local_rhea_id, make_dataframe, make_global_rhea_id

chebi_name_df = None
is_a_df = None

ec_df = None
ecocyc_df = None
kegg_df = None
macie_df = None
metacyc_df = None
reactome_df = None
rhea_name_df = None

def rhea2reactome(rhea_id:str) -> List[str]:
    global reactome_df

    if reactome_df is None:
        reactome_df = make_dataframe(filename='rhea2reactome.tsv', index='RHEA_ID')

    rhea_id = make_local_rhea_id(rhea_id)

    try:
        result = reactome_df.loc[rhea_id]['ID']

        if isinstance(result, str):
            return ["Reactome:"+result]
        else:
            return ["Reactome:"+name for name in result]
    except:
        return []

def rhea2metacyc(rhea_id:str) -> str:
    global metacyc_df

    if metacyc_df is None:
        metacyc_df = make_dataframe(filename='rhea2metacyc.tsv', index='RHEA_ID')

    rhea_id = make_local_rhea_id(rhea_id)

    try:
        return "MetaCyc:" + metacyc_df.loc[rhea_id].at['ID']
    except KeyError:
        return None

def rhea2macie(rhea_id:str) -> str:
    global macie_df

    if macie_df is None:
        macie_df = make_dataframe(filename='rhea2macie.tsv', index='RHEA_ID')

    rhea_id = make_local_rhea_id(rhea_id)

    try:
        return "MACiE:" + macie_df.loc[rhea_id].at['ID']
    except KeyError:
        return None

def rhea2kegg(rhea_id:str) -> str:
    global kegg_df

    if kegg_df is None:
        kegg_df = make_dataframe(filename='rhea2kegg_reaction.tsv', index='RHEA_ID')

    rhea_id = make_local_rhea_id(rhea_id)

    try:
        return "KEGG:" + kegg_df.loc[rhea_id].at['ID']
    except KeyError:
        return None

def rhea2ecocyc(rhea_id:str) -> str:
    global ecocyc_df

    if ecocyc_df is None:
        ecocyc_df = make_dataframe(filename='rhea2ecocyc.tsv', index='RHEA_ID')

    rhea_id = make_local_rhea_id(rhea_id)

    try:
        return "EcoCyc:" + ecocyc_df.loc[rhea_id].at['ID']
    except KeyError:
        return None

def rhea2ec(rhea_id:Union[str, int]) -> str:
    global ec_df

    if ec_df is None:
        ec_df = make_dataframe(filename='rhea2ec.tsv', index='RHEA_ID')

    rhea_id = make_local_rhea_id(rhea_id)

    try:
        return "EC:" + ec_df.loc[rhea_id].at['ID']
    except KeyError:
        return None

def is_a(rhea_id:Union[str, int]) -> str:
    global is_a_df

    if is_a_df is None:
        is_a_df = make_dataframe(filename='rhea-relationships.tsv', index='FROM_REACTION_ID')

    rhea_id = make_local_rhea_id(rhea_id)

    try:
        return "RHEA:" + str(is_a_df.loc[rhea_id].at['TO_REACTION_ID'])
    except KeyError:
        return None

def chebi2name(chebiId:str) -> str:
    global chebi_name_df

    if chebi_name_df is None:
        chebi_name_df = make_dataframe(
            filename='chebiId_name.tsv',
            index='chebiId',
            header=None,
            names=['chebiId', 'name']
        )

    chebiId = make_curie(chebiId, 'CHEBI')

    try:
        return chebi_name_df.loc[chebiId].at['name'].strip()
    except KeyError:
        return None

def rhea2name(rhea_id:str) -> str:
    global rhea_name_df
    if rhea_name_df is None:
        rhea_name_df = make_dataframe(filename='rhea2name.tsv', index='RHEA_ID')

    rhea_id = make_global_rhea_id(rhea_id)

    try:
        return rhea_name_df.loc[rhea_id].at['Name']
    except KeyError:
        return None
