# Stand-alone file to parse and save RHEA reaction ids to names in a TSV file
# Command line use:
#   `python rhea_to_name_parser.py 10000 10005` will collect names from RHEA:10000 to 10005
#   `python rhea_to_name_parser.py` will collect names from RHEA:10000 to 56987

import sys
import requests
import xml.etree.ElementTree as etree
import csv 

API_RXN = 'https://www.rhea-db.org/rest/1.0/ws/reaction/biopax2/'
BP = "{http://www.biopax.org/release/biopax-level2.owl#}"

def harvest_names(start, end):
    """
    Collects the human-readable formulas of the RHEA reaction from given start to end indices.
    As of Aug 16, 2018 - RHEA appears to have reactions listed from 10000 to 56987
    """
    file_name = "rhea2name_" + str(start) + "_" + str(end) + ".tsv"
    file_name_err = file_name[:-4] + "_errors.tsv"

    error_ids = []
    with open(file_name, 'w') as tsvfile, open(file_name_err, 'w') as errorfile:
        writer = csv.writer(tsvfile, delimiter='\t')
        writer.writerow(["RHEA_ID", "Name"])
        err_writer = csv.writer(errorfile, delimiter='\t')
        err_writer.writerow(["RHEA_ID", "Info"])
        for i in range(start, end+1):
            str_i = str(i)
            try:
                response = requests.get(API_RXN + str_i)
                content = response.content
                e = etree.fromstring(content)
                name = get_name(e)

                writer.writerow(["RHEA:" + str_i, name])
                if i % 5 == 0:
                    print("[Recording every 5] Processed RHEA:" + str_i + " == " + name)
            except etree.ParseError:
                if "Not found" in str(content):
                    print("LOG - RHEA: " + str_i + " does not exist")
                    err_writer.writerow(["RHEA:" + str_i, "DNE"])
                else:
                    print("ERROR: could not get name for RHEA: " + str_i)
                    err_writer.writerow(["RHEA:" + str_i, "parse error"])
            except:
                print("ERROR: could not get name for RHEA: " + str_i)
                err_writer.writerow(["RHEA:" + str_i, "error"])

def get_rxn_tag(e):
    """
    Finds the bp:biochemicalReaction tag from an XML Element. If not found, tries to find the 
    bp:transport tag (since some reactions use that tag). Returns None if not found.
    """
    rxn_el = e.find(BP + "biochemicalReaction")
    if rxn_el is None:
        rxn_el = e.find(BP + "transport")
        if rxn_el is None:
            rxn_el = e.find(BP + "transportWithBiochemicalReaction")
    return rxn_el

def get_name_from_rxn_tag(e):
    """
    Finds the bp:NAME tag from within a bp:biochemicalReaction. Returns None if not found.
    """
    return e.findtext(BP + "NAME")

def get_name(e):
    """
    Finds the bp:NAME tag from within the root element. Returns None if not found.
    """
    el = get_rxn_tag(e)
    return get_name_from_rxn_tag(el)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        harvest_names(int(sys.argv[1]), int(sys.argv[2]))