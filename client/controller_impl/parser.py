import requests
import xml.etree.ElementTree as etree

# RHEA API endpoints
API_SEARCH = 'https://www.rhea-db.org/rest/1.0/ws/reaction/biopax2?q='
API_RXN = 'https://www.rhea-db.org/rest/1.0/ws/reaction/biopax2/'

# Curie namespaces
EC = "EC:"
RHEA = "RHEA:"
CHEBI = "CHEBI:"
GENERIC = "GENERIC:"

NAMESPACES = [EC, RHEA, CHEBI, GENERIC]

# XML namespaces
#TODO: should maybe be getting this from the document instead of hardcoding it
BP = "{http://www.biopax.org/release/biopax-level2.owl#}"
RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
PMID = "https://www.ncbi.nlm.nih.gov/pubmed/"

CTRL_TAG = "#rel/controller/"

# Reaction Categories
RHEA_RXN_CATEGORIES = ["molecular activity"]
EC_RXN_CATEGORIES = ["genomic entity"]
CHEBI_RXN_CATEGORIES = ["molecular entity"]

RHEA_RXN_CAT_DESCR = "an execution of a molecular function carried out by a gene product or macromolecular complex" 
EC_RXN_CAT_DESCR = "an entity that can either be directly located on a genome (gene, transcript, exon, regulatory region) or is encoded in a genome (protein)"
CHEBI_RXN_CAT_DESCR = "a gene, gene product, small molecule or macromolecule (including protein complex)"

# Relationship Edge Labels
RXN_TO_MOL = "has_participant"
MOL_TO_MOL = "interacts_with"
RXN_TO_RXN = "overlaps"

RXN_TO_MOL_DESCR = "holds between a process and a continuant, where the continuant is somehow involved in the process"
RXN_TO_RXN_DESCR = "holds between entities that overlap in their extents (materials or processes)"



RHEA_WEB_URI = "https://www.rhea-db.org/reaction?id="


def query_search(search_term):
    """
    Searches for given id and returns root Element of search results document. Returns None if error was 
    thrown during API call
    """
    if startswith_ec(search_term):
        response = requests.get(API_SEARCH + search_term[3:])
    else:
        response = requests.get(API_SEARCH + search_term)
    if response.status_code == 404:
        print("Could not find search term: " + search_term)
        return None
    elif response.status_code != 200:
        print("APIException for " + search_term + ": " + response.url + " returned status code: " + str(response.status_code))
        return None
    else:
        return etree.fromstring(response.content)

def query_concept(search_id):
    """
    Searches for given id and returns root Element of reaction details document (in Biopax2 XML). 
    Returns None if error was thrown during API call
    """
    if startswith_rhea(search_id):
        response = requests.get(API_RXN + search_id[5:])
    else:
        response = requests.get(API_RXN + search_id)
    if response.status_code == 404:
        print("Could not find search id: " + search_id)
        return None
    if response.status_code != 200:
        print("APIException: " + response.url + " returned status code: " + str(response.status_code))
        return None
    else:
        return etree.fromstring(response.content)

def startswith_rhea(s):
    return s.upper().startswith(RHEA)

def startswith_ec(s):
    return s.upper().startswith(EC)

def startswith_chebi(s):
    return s.upper().startswith(CHEBI)

def startswith_generic(s):
    return s.upper().startswith(GENERIC)

def is_comment_tag(tag):
    return tag == BP + "COMMENT"

def is_xref_tag(tag):
    return tag == BP + "XREF"

def is_ec_tag(tag):
    return tag == BP + "EC-NUMBER"

def get_controller(xref_el):
    text = xref_el.attrib[RDF + "resource"]
    if text.startswith(CTRL_TAG):
        return text[len(CTRL_TAG):]
    else:
        return None


def get_rxn_tag(e):
    """
    Finds the bp:biochemicalReaction tag from an XML Element. If not found, tries to find other tags
    that could be used. Returns None if not found.
    """
    rxn_el = e.find(BP + "biochemicalReaction")
    if rxn_el is None:
        rxn_el = e.find(BP + "transport")
        if rxn_el is None:
            rxn_el = e.find(BP + "transportWithBiochemicalReaction")
    return rxn_el

def get_name_from_tag(e):
    """
    Finds the human-readable name from bp:NAME tag from within another tag. Returns None if not found.
    """
    return e.findtext(BP + "NAME")

def get_name(e):
    """
    Finds the human-readable name from bp:NAME tag from within the root element. Returns None if not found.
    """
    el = get_rxn_tag(e)
    return get_name_from_tag(el)
    # name_el = e.find(BP+"biochemicalReaction/" + BP+"NAME")
    # if name_el is None:
    #     name_el = e.find(BP+"transport/" + BP+"NAME")
    # return name_el.text

def get_rhea_ids(root):
    """
    Returns list of RHEA curie ids from search results root Element
    """
    results = []
    for el in root.iterfind("./resultset/rheaReaction/rheaid/id"):
        rhea_id = el.text
        results.append(RHEA + rhea_id)
    return results

def get_ec_ids(root):
    """
    Returns list of EC ids from EC-NUMBER tag
    """
    ec_ids = []
    for enzyme in root.iterfind(BP+"biochemicalReaction/" + BP+"EC-NUMBER"):
        ec_ids.append(EC + enzyme.text)
    return ec_ids


def get_molecules(root):
    """
    Returns list of molecule dictionaries from search results root Element
    """
    molecules=[]
    for molecule in root.iter(BP + "physicalEntity"):
        name = get_name_from_tag(molecule)
        m_id, m_type, residue = [None]*3
        for elem in molecule.iter(BP+'COMMENT'):
            text = elem.text
            if text.startswith('ACCESSION:'):
                m_id = get_mol_comment(text)
            elif text.startswith('COMPOUND_TYPE:'):
                m_type = get_mol_comment(text)
            elif text.startswith('RESIDUE_POSITION:'):
                # only exists for generic molecules
                residue = get_mol_comment(text)
        
        molecules.append({
            "m_id": m_id,
            "name": name,
            "type": m_type,
            "residue": residue 
        })
    return molecules

def get_mol_comment(text:str):
    text = text.split(":",1)[1]
    if text.startswith(" "):
        text = text[1:]
    return text

def get_related_rhea_rxns(root):
    """
    Returns related list of RHEA reaction dicts from root Element
    """
    # reactions = [rxn for rxn in e.findall(BP+'relationshipXref') if RHEA_PREFIX in elem.attrib[RDF+"about"]]
    rxns = []
    for reaction in root.iter(BP+"relationshipXref"):
        if reaction.find(BP+"DB-VERSION") is not None:
            rxn_id = RHEA + reaction.findtext(BP+"ID")
            relation=reaction.findtext(BP+"RELATIONSHIP-TYPE")

            rxns.append({
                "r_id": rxn_id,
                "relation": relation
            })
    return rxns
        


def get_evidence(e):
    """
    Returns list of evidence details dictionaries
    """
    evidence = []
    for pub in e.findall(BP+"publicationXref"):
        name = pub.findtext(BP+"TITLE")
        date = pub.findtext(BP+"YEAR")
        p_id = pub.findtext(BP+"ID")
        uri = PMID+p_id if pub.findtext(BP+"DB") == "PubMed" else None
        evidence.append({
            "name": name,
            "date": date,
            "p_id": p_id,
            "uri": uri 
        })
    return evidence

def get_num_of_results(root):
    result = root.find("resultset")
    if result is not None:
        return int(result.attrib["numberofrecordsreturned"])
    else:
        return 0


def in_namespace(concept_id):
    """
    Returns True if given CURIE concept id is in any of the possible namespaces from RHEA, False otherwise
    """
    concept_id = concept_id.upper()
    concept_components = concept_id.split(":")
    namespace = concept_components[0] + ":"
    return namespace in NAMESPACES
