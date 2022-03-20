from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions
from util import constants, helpers

class API(SPARQLWrapper):
    def __init__(self) -> None:
        super().__init__(constants.URL)
        self._prefixes = {}
        self.prefixes = {}

    def addPrefix(self, prefix):
        # print(len(keys), prefix)
        # print(self._prefixes)
        i = len(self._prefixes.keys())
        if self._prefixes.get(prefix):
            i = self._prefixes[prefix][1]
        self._prefixes[prefix] = ('x', i)
        self.prefixes = [f'PREFIX {x + str(i)}: <{prefix}>' for (prefix, (x, i)) in self._prefixes.items()]

    def queryTest(self, query):
        try:
            self.setQuery(query)
            self.setReturnFormat(JSON)
            results = self.query().convert()
        except:# SPARQLExceptions.QueryBadFormed as e :
            # e = sys.exc_info()[0]
            # print('ERROR: ', e)
            return {'results': {'bindings': []}}
        return results

    # by default we select all entities of type ?o. You can pass a query to change this behaviour.
    def queryKG(self, query="""select * where { ?s a ?o .
                                               BIND(<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> AS ?p) }"""):
        # print(self.prefixes)
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
        # print(variables)
        for result in results["results"]["bindings"]:
            for keys in variables:
                if set(keys) == set(result.keys()): # this checked only n times, where n is the length of variables
                    spo = []
                    for i in range(len(keys)):
                        key = result[keys[i]]
                        if i == 0 and 'schema' in key['value']:
                            break
                        spo.append(key)
                    # spo = [result[keys[i]] for i in range(len(keys)) if i == 0 and not ('schemas' in result[keys[i]]['value'])]
                    # if p is comment remove
                    # spo before: {type, value }
                    for x in spo:
                       # sPrefix, pPrefix, oPrefix
                        x['prefix'] = helpers.parsePrefixes([x])[0]
                        x['value'] = helpers.parseTriple([x])[0]
                        self.addPrefix(x['prefix'])
                        pref = self._prefixes[x['prefix']][0] + str(self._prefixes[x['prefix']][1])
                        x['prefix_entity'] = f"{pref}:{x['value']}"
                    # spo after: {type, value, prefix}
                    output.append(spo)
                    # print(spo)
        return output