from enum import Enum

class Category(Enum):
    chemical_substance=['CHEBI', 'GENERIC', 'POLYMER']
    protein=['EC']
    molecular_activity=['RHEA']

    def __init__(self, prefixes):
        self.prefixes = prefixes

    @property
    def name(self):
        return super().name.replace('_', ' ')

class Predicate(Enum):
    def __init__(self, d):
        self.domain = d['domain']
        self.codomain = d['codomain']
        self.edge_label = d['edge_label'] if 'edge_label' in d and d['edge_label'] is not None else 'related_to'
        self.relation = d['relation'] if 'relation' in d and d['relation'] is not None else self.edge_label
        self.__sparql__ = d['sparql']

    @property
    def sparql(self):
        """
        Returns the sparql query for this kind of edge, appending the appropriate
        bindings.
        """
        return f"""
        {{
            {self.__sparql__}
            BIND("{self.edge_label}" AS ?edge_label) .
            BIND("{self.relation}" AS ?relation) .
        }}
        """

    @property
    def sparql_with_citations(self):
        """
        Returns the sparql query for this kind of edge, appending the appropriate
        bindings and citation query.

        If ?relation is not declared in the base query then no citation data
        is gathered. Citations are only attached to relations.
        """
        if '?reaction' not in self.__sparql__:
            return self.sparql
        else:
            return f"""
            {{
                {self.__sparql__}
                BIND("{self.edge_label}" AS ?edge_label) .
                BIND("{self.relation}" AS ?relation) .
                OPTIONAL {{ ?reaction rh:citation ?citation }} .
            }}
            """

    molecularly_interacts_with=dict(
        domain=Category.chemical_substance,
        codomain=Category.chemical_substance,
        edge_label='molecularly_interacts_with',
        relation='participates in the same reaction side as',
        sparql="""
        ?reaction rdfs:subClassOf rh:Reaction .
        ?reaction rh:status rh:Approved .
        ?reaction rh:side ?side .
        ?side rh:contains ?p1 .
        ?side rh:contains ?p2 .
        FILTER (?p1 != ?p2) .
        ?p1 rh:compound ?c1 .
        ?p2 rh:compound ?c2 .

        ?c1 rh:name ?subjectName .
        ?c1 rh:accession ?subjectId .

        ?c2 rh:name ?objectName .
        ?c2 rh:accession ?objectId .
        """
    )

    derives_into=dict(
        domain=Category.chemical_substance,
        codomain=Category.chemical_substance,
        edge_label='derives_into',
        relation='participates in the opposite reaction side as',
        sparql="""
        ?reaction rdfs:subClassOf rh:Reaction .
        ?reaction rh:status rh:Approved .
        ?reaction rh:side ?side1 .
        ?reaction rh:side ?side2 .

        ?side1 rh:curatedOrder 1 .
        ?side2 rh:curatedOrder 2 .

        ?side1 rh:contains ?p1 .
        ?side2 rh:contains ?p2 .

        ?p1 rh:compound ?compound1 .
        ?p2 rh:compound ?compound2 .

        ?compound1 rh:accession ?subjectId .
        ?compound1 rh:name ?subjectName .

        ?compound2 rh:accession ?objectId .
        ?compound2 rh:name ?objectName .
        """
    )

    increases_synthesis_of=dict(
        domain=Category.protein,
        codomain=Category.chemical_substance,
        edge_label='increases_synthesis_of',
        relation='probably increases synthesis (might increase degradation) of',
        sparql="""
        ?reaction rdfs:subClassOf rh:Reaction .
        ?reaction rh:status rh:Approved .
        ?reaction rh:ec ?subjectId .
        ?reaction rh:side ?side .
        ?side rh:curatedOrder 2 .
        ?side rh:contains ?p .
        ?p rh:compound ?compound .

        ?compound rh:name ?objectName .
        ?compound rh:accession ?objectId .
        """
    )

    increases_degradation_of=dict(
        domain=Category.protein,
        codomain=Category.chemical_substance,
        edge_label='increases_degradation_of',
        relation='probably increases degradation (might increase synthesis) of',
        sparql="""
        ?reaction rdfs:subClassOf rh:Reaction .
        ?reaction rh:status rh:Approved .
        ?reaction rh:ec ?subjectId .
        ?reaction rh:side ?side .
        ?side rh:curatedOrder 1 .
        ?side rh:contains ?p .
        ?p rh:compound ?compound .

        ?compound rh:name ?objectName .
        ?compound rh:accession ?objectId .
        """
    )

    participates_in=dict(
        domain=Category.chemical_substance,
        codomain=Category.molecular_activity,
        edge_label='participates_in',
        sparql="""
        ?reaction rdfs:subClassOf rh:Reaction .
        ?reaction rh:status rh:Approved .
        ?reaction rh:side ?side .
        ?side rh:contains ?participant .
        ?participant rh:compound ?compound .

        ?reaction rh:equation ?objectName .
        ?reaction rh:accession ?objectId .

        ?compound rh:name ?subjectName .
        ?compound rh:accession ?subjectId .
        """
    )

    increases_activity_of=dict(
        domain=Category.protein,
        codomain=Category.molecular_activity,
        edge_label='increases_activity_of',
        sparql="""
        ?reaction rdfs:subClassOf rh:Reaction .
        ?reaction rh:status rh:Approved .
        ?reaction rh:ec ?subjectId .

        ?reaction rh:equation ?objectName .
        ?reaction rh:accession ?objectId .
        """
    )

    catalyzes_same_reaction=dict(
        domain=Category.protein,
        codomain=Category.protein,
        relation='catalyzes same reaction as',
        sparql="""
        ?reaction rdfs:subClassOf rh:Reaction .
        ?reaction rh:status rh:Approved .
        ?reaction rh:ec ?subjectId .
        ?reaction rh:ec ?objectId .

        FILTER (?subjectId < ?objectId) .
        """
    )

    has_same_catalyst=dict(
        domain=Category.molecular_activity,
        codomain=Category.molecular_activity,
        relation='has same catalyst',
        sparql="""
        ?reaction1 rdfs:subClassOf rh:Reaction .
        ?reaction1 rh:status rh:Approved .

        ?reaction2 rdfs:subClassOf rh:Reaction .
        ?reaction2 rh:status rh:Approved .

        ?reaction1 rh:ec ?enzyme .
        ?reaction2 rh:ec ?enzyme .

        FILTER (?reaction1 < ?reaction2) .

        ?reaction1 rh:accession ?subjectId .
        ?reaction2 rh:accession ?objectId .

        ?reaction1 rh:equation ?subjectName .
        ?reaction2 rh:equation ?objectName .
        """
    )

    def matches(self, edge_label, relation, subject_categories, object_categories):
        """
        Check that the filters (None value means no filter) match the edges
        edge_label and relation.
        """
        if edge_label is not None:
            if self.edge_label.lower() != edge_label.lower():
                return False

        if relation is not None:
            if self.relation.lower() != relation.lower():
                return False

        if subject_categories is not None:
            if not any(c.lower() == self.domain.name.lower() for c in subject_categories):
                return False

        if object_categories is not None:
            if not any(c.lower() == self.codomain.name.lower() for c in object_categories):
                return False

        return True

if __name__ == '__main__':
    print('Edge label:', Edge.catalyzes_same_reaction.edge_label)
    print('Relation:', Edge.catalyzes_same_reaction.relation)


    from collections import defaultdict

    d = defaultdict(set)

    for edge in Edge:
        print(edge)
        d[edge.domain.name + ' -> ' + edge.codomain.name].add(edge.relation)

    for key, value in d.items():
        print()
        print(key)
        print(value)
