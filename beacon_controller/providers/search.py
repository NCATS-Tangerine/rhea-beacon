import pandas as pd
import re
from typing import List, Union, Dict


def search(df:pd.DataFrame, columns:Union[List[str], str], keywords:Union[List[str], str], column_multiplier:Dict[str, int]=None, unique_columns:Union[List[str], str]=None, offset=None, size=None, metadata=False):
    if isinstance(columns, str):
        columns = [columns]
    elif not isinstance(columns, list):
        raise Exception(f'Columns must be of type string or list of strings, not {type(columns)}')

    if isinstance(keywords, str):
        keywords = [keywords]
    elif not isinstance(keywords, list):
        keywords = []

    if not isinstance(column_multiplier, dict):
        column_multiplier = {}

    q = df.apply(lambda x: False, axis=1)
    for column in columns:
        for keyword in keywords:
                q |= df[column].str.contains(keyword, case=False, regex=False)

    result = df[q == True]

    result = result.drop_duplicates(subset=unique_columns)

    def count(row):
        c = 0
        for column in columns:
            m = 1 if column not in column_multiplier else column_multiplier[column]
            value = row[column]
            if isinstance(value, str):
                for keyword in keywords:
                    keyword, value = keyword.lower(), value.lower()
                    c += value.count(keyword) * m
        return c

    if max(result.shape) == 0:
        result['search_score'] = result.apply(count, axis=1)
        result = result.sort_values(by=['search_score'], ascending=False)

    total_num_rows = result.shape[0]

    if offset is not None:
        result = result.iloc[offset:]
    if size is not None:
        result = result.iloc[:size]

    if metadata:
        return result.to_dict(orient='records'), total_num_rows
    else:
        return result.to_dict(orient='records')