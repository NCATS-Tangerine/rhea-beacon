# https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=10684596,12753071&retmode=json&tool=knowledge_beacon&email=lance@starinformatics.com

import requests
from time import time, sleep
from typing import List, Union

BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi'
URI='http://rdf.ncbi.nlm.nih.gov/pubmed/'

def partition_generator(l, n):
    """https://stackoverflow.com/a/312464/4750502"""
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

class PubMedRetreiver(object):
    """
    This object makes at most three requests per second.

    In the future this should be extended to retreive abstracts too.
    """

    def __init__(self, email, tool='knowledge_beacon', retmode='json'):
        self.tool = tool
        self.email = email
        self.retmode = retmode
        self.last_time = time()

    def get(self, pmid:Union[List[str], str]) -> dict:
        if isinstance(pmid, str):
            return get([pmid])
        elif isinstance(pmid, list):
            pmids = [p.upper().replace('PMID:', '').replace('PUBMED:', '').replace(URI.upper(), '') for p in pmid]

            d = {}

            for pmids in partition_generator(pmids, 50):
                params = dict(
                    db='pubmed',
                    retmode=self.retmode,
                    id=','.join(pmids),
                    tool=self.tool,
                    email=self.email
                )

                delta = time() - self.last_time
                if delta < 1/3.0:
                    sleep(1/3.0 - delta)

                response = requests.get(BASE_URL, params=params)

                self.last_time = time()

                if response.ok:
                    d.update(response.json().get('result'))

            return d
