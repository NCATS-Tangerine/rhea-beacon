import rhea as rh

if __name__ == '__main__':
    assert(rh.chebi2name('CHEBI:368997') == 'N-benzyloxycarbonylglycine')
    assert(rh.is_a('53555') == '53563')
    assert(rh.rhea2ec('10528') == '1.14.14.100')
    assert(rh.rhea2ecocyc('10489') == '5-FORMYL-THF-CYCLO-LIGASE-RXN')
    assert(rh.rhea2kegg('10707') == 'R03665')
    assert(rh.rhea2macie('16882') == 'M0153')
    assert(rh.rhea2metacyc('10085') == 'PROTOCATECHUATE-34-DIOXYGENASE-RXN')

    reactome = rh.rhea2reactome('11393')
    assert('R-HSA-1855218.2' in reactome)
    assert('R-HSA-1855213.2' in reactome)
    assert(len(reactome) == 2)

    print(rh.rhea2reactome('11597'))
    print(rh.rhea2reactome('11685'))

    print('All passed')
