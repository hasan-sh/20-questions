# import requests
from msilib.schema import SelfReg
from SPARQLWrapper import SPARQLWrapper, JSON
from util import constants
import time

class API(SPARQLWrapper):
    def __init__(self) -> None:
        super().__init__(constants.URL)

    # by default we select all entities of type ?o. You can pass a query to change this behaviour.
    def queryKG(self, query="""select * where { ?s a ?o .
                                                BIND('rdf:type' AS ?p)
                                                }"""):
        self.setQuery(query)
        self.setReturnFormat(JSON)
        results = self.query().convert()
        return results
    # the variables should be compatible with whatever variables you want to extract from the query.
    def parseJSON(self, results, variables=[['s', 'p', 'o']]):
        output = []
        for result in results["results"]["bindings"]:
            spo = [result[key]['value'] for keys in variables for key in keys]
            output.append(spo)
        return output

# t = time.process_time()
# # graph = initializeGame(fileName)
# a = API()
# r = a.queryKG()
# elapsed_t = time.process_time() - t
# print(elapsed_t)
# a.parseJSON(r)