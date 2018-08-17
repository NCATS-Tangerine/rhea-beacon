import pandas as pd
from pandas import DataFrame

import os

_ROOT = os.path.abspath(os.path.dirname(__file__))

def get_data_path(filename:str) -> str:
    """
    Gets the path of a file in the data directory
    """
    return os.path.join(_ROOT, 'data', filename)

def make_curie(local_id:str, prefix:str) -> str:
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

def make_dataframe(filename:str, index, header='infer', names=None) -> DataFrame:
    data_path = get_data_path(filename)
    df = pd.read_csv(data_path, sep='\t', header=header, names=names, dtype=str)
    if index != None:
        df = df.set_index(index)
    return df
