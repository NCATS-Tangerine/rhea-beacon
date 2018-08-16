import pandas as pd

chebiId_name_df = None

def process(identifier:str, prefix) -> str:
    if ':' not in identifier:
        identifier = '{}:{}'.format(prefix, identifier)

    return identifier.upper()

def chebi2name(chebiId:str) -> str:
    global chebiId_name_df

    if chebiId_name_df == None:
        chebiId_name_df = pd.read_csv(
            'rhea/chebiId_name.tsv',
            sep='\t',
            header=None,
            names=['chebiId', 'name']
        )

        chebiId_name_df = chebiId_name_df.set_index(['chebiId'])

    chebiId = process(chebiId, 'CHEBI')

    return chebiId_name_df.loc[chebiId].at['name'].strip()



if __name__ == '__main__':
    chebiId = 'CHEBI:368997'

    name = chebi2name(chebiId)

    print(chebiId, '-->', name)

    assert(name == 'N-benzyloxycarbonylglycine')
