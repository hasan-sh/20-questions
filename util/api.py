from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions
from util import constants

class API(SPARQLWrapper):
    def __init__(self) -> None:
        super().__init__(constants.URL)

    # by default we select all entities of type ?o. You can pass a query to change this behaviour.
    def queryKG(self, query="""select * where { ?s a ?o .
                                                BIND('http://www.w3.org/1999/02/22-rdf-syntax-ns#type' AS ?p) }"""):
        
        try:
            self.setQuery(query)
            self.setReturnFormat(JSON)
            results = self.query().convert()
        except:# SPARQLExceptions.QueryBadFormed as e :
            # e = sys.exc_info()[0]
            # print('ERROR: ', e)
            return {'results': {'bindings': []}}
        return results
        
    # the variables should be compatible with whatever variables you want to extract from the query.
    def parseJSON(self, results, variables=[['s', 'p', 'o']]):
        output = []

        for result in results["results"]["bindings"]:
            for keys in variables:
                if set(keys) == set(result.keys()): # this checked only n times, where n is the length of variables
                    spo = [result[key] for key in keys]
                    output.append(spo)
        return output