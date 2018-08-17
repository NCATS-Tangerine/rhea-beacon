# RHEA Beacon

This package contains methods for utilizing some Rhea data files (https://www.rhea-db.org/download).

### Installation

```shell
virtualenv -p python3.5 venv
source venv/bin/activate
python setup.py install
```

### Use

For the functions that map a rhea identifier to another identifier, curies are not used. It's assumed that the identifer is a RHEA identifier. For `chebi2name` a CHEBI curie can be used, otherwise it's assumed the identifer is a CHEBI identifier.

```python
>>> import rhea as rh
>>> rh.chebi2name('CHEBI:368997')
'N-benzyloxycarbonylglycine'
>>> rh.chebi2name('368997')
'N-benzyloxycarbonylglycine'
>>> rh.is_a('53555')
'53563'
>>> rh.rhea2ec('10528')
'1.14.14.100'
>>> rh.rhea2ecocyc('10489')
'5-FORMYL-THF-CYCLO-LIGASE-RXN'
>>> rh.rhea2kegg('10707')
'R03665'
>>> rh.rhea2macie('16882')
'M0153'
>>> rh.rhea2metacyc('10085')
'PROTOCATECHUATE-34-DIOXYGENASE-RXN'
>>> rh.rhea2reactome('11393')
['R-HSA-1855213.2', 'R-HSA-1855218.2']
```
