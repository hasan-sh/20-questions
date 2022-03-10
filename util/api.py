# import requests
# from msilib.schema import SelfReg
# from tokenize import Triple
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import RDF
from util import constants
import time

class API(SPARQLWrapper):
    def __init__(self) -> None:
        super().__init__(constants.URL)

    # by default we select all entities of type ?o. You can pass a query to change this behaviour.
    def queryKG(self, query="""select * where { ?s a ?o .
                                                BIND('http://www.w3.org/1999/02/22-rdf-syntax-ns#type' AS ?p) }"""):
        self.setQuery(query)
        self.setReturnFormat(JSON)
        results = self.query().convert()
        return results
        
    # the variables should be compatible with whatever variables you want to extract from the query.
    def parseJSON(self, results, variables=[['s', 'p', 'o']]):
        output = []

        for result in results["results"]["bindings"]:
            for keys in variables:
                if set(keys) == set(result.keys()): # this checked only n times, where n is the length of variables
                    spo = [result[key]['value'] for key in keys]
                    output.append(spo)
        return output

# t = time.process_time()
# # graph = initializeGame(fileName)
# a = API()
# r = a.queryKG()
# elapsed_t = time.process_time() - t
# print(elapsed_t)
# a.parseJSON(r)