"""
Download page: ftp://ftp.expasy.org/databases/enzyme
Explanation of data file and line types: ftp://ftp.expasy.org/databases/enzyme/enzuser.txt
"""

import requests, os

path = 'ftp://ftp.expasy.org/databases/enzyme/enzyme.dat'

print('Downloading ' + path)

if not os.path.exists('enzyme.dat'):
    try:
        import urllib.request
        urllib.request.urlretrieve(path, 'enzyme.dat')
    except:
        import urllib
        urllib.urlretrieve(path, 'enzyme.dat')
    finally:
        if not os.path.exists('enzyme.dat'):
            quit('Could not download {path}'.format(path))

q="""
PREFIX rh:<http://rdf.rhea-db.org/>
PREFIX ch:<http://purl.obolibrary.org/obo/>
SELECT distinct ?ec WHERE {
  ?reaction rdfs:subClassOf rh:Reaction .
  ?reaction rh:ec ?ec .
}
order by ?ec
"""

print('Getting enzymes')

response = requests.get(
    url="https://sparql.rhea-db.org/sparql",
    params={
        'query': q,
        'format' : 'application/sparql-results+json'
    }
)

enzymes = []
for binding in response.json().get('results').get('bindings'):
    enzymes.append(binding.get('ec').get('value').replace('http://purl.uniprot.org/enzyme/', ''))

print('Building CSV')

IDENTIFICATION = 'ID'
TERMINATION = '//'
ALTERNATE_NAMES = 'AN'
DESCRIPTION = 'DE'

written = 0
with open('enzyme.dat', 'r') as f:
    open("ecc_names.csv", "w+").close()
    with open("ecc_names.csv", "a+") as output_file:
        output_file.write('ID\tName\tSynonyms\n')
        d = None
        for line in f:
            components = line.split()

            if len(components) == 1 and components[0] == TERMINATION:
                line_type = TERMINATION
            elif len(components) > 1:
                line_type = components[0]
                line_content = ' '.join(components[1:])
            else:
                continue

            if line_type == IDENTIFICATION:
                d = {'id' : line_content}
            elif line_type == DESCRIPTION and d is not None:
                if line_content == 'Deleted entry.':
                    d = None
                else:
                    d['name'] = line_content
            elif line_type == ALTERNATE_NAMES and d is not None:
                if 'synonyms' not in d:
                    d['synonyms'] = list()
                d['synonyms'].append(line_content)
            elif line_type == TERMINATION and d is not None:
                i, n, s = d.get('id', ''), d.get('name', ''), d.get('synonyms', [])
                if i in enzymes:
                    s = ';'.join(s)
                    output_file.write('{i}\t{n}\t{s}\n'.format(i=i, n=n, s=s))

                    written += 1

print('Written:', written, ', Total enzymes in Rhea:', len(enzymes))

os.remove('enzyme.dat')

if not os.path.exists('enzyme.dat'):
    print('Successfully removed enzyme.dat')
else:
    print('Failed to remove enzyme.dat')
