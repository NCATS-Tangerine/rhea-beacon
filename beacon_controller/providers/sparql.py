from typing import List

class SparqlBuilder(object):
    def __init__(self, select:List[str], size=None, offset=None):
        self.query = f"""
        PREFIX rh:<http://rdf.rhea-db.org/>
        SELECT
          {' '.join([f'?{s}' for s in select])}
        WHERE {{

        }}
        """
