import re
import sys
from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions, POST
from util import constants, helpers

class API(SPARQLWrapper):
    """
    TODO: Document

    """
    def __init__(self) -> None:
        super().__init__(constants.URL)
        self._prefixes = {}
        self.prefixes = {}
        self.memory = {}

    def addPrefix(self, prefix):
        """
        TODO: Document

        """
        i = len(self._prefixes.keys())
        if self._prefixes.get(prefix):
            i = self._prefixes[prefix][1]
        self._prefixes[prefix] = ('x', i)
        self.prefixes = [f'PREFIX {x + str(i)}: <{prefix}>' for (prefix, (x, i)) in self._prefixes.items()]

    # by default we select all entities of type ?o. You can pass a query to change this behaviour.
    def queryKG(self, query="""select * where { ?s a ?o .
                                               BIND(<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> AS ?p) }"""):
        """
        TODO: Document

        """
        try:
            self.setQuery(query)
            self.setReturnFormat(JSON)
            self.setMethod(POST)
            results = self.query().convert()
        except:# SPARQLExceptions.QueryBadFormed as e :
            e = sys.exc_info()[0]
            print('ERROR: ', e)
            print(query)
            return {'results': {'bindings': []}}
        return results
        
    # the variables should be compatible with whatever variables you want to extract from the query.
    def parseJSON(self, results, variables=[['s', 'p', 'o']]):
        """
        TODO: Document

        """
        output = []
        for result in results["results"]["bindings"]:
            for keys in variables:
                if set(keys) == set(result.keys()): # this checked only n times, where n is the length of variables
                    spo = []
                    for i in range(len(keys)):
                        key = result[keys[i]]
                        if 's' in keys[i] and 'schema' in key['value']: # only if the subject is from schema; this is because the subject here binds the p and o.
                           break
                        spo.append(key)

                    for x in spo:
                        if x['value'] in self.memory: # if already parsed and in memory
                            x = self.memory[x['value']]

                    for x in spo:
                        if len(x.keys()) <= 3: # if not yet parsed
                            x['uri'] = x['value']
                            if x['type'] != 'literal': # add prefixes only for non literals.
                                # if ("'" or "-") in x['value']: # some characters shouldn't be escaped, take full URI instead
                                value = helpers.parseTriple([x])
                                if re.search(r"[', - –]", value[0]): # some characters shouldn't be escaped, take full URI instead
                                    x['prefix_entity'] = f"<{x['uri']}>"
                                else:
                                    x['prefix'] = helpers.parsePrefixes([x])[0]
                                    self.addPrefix(x['prefix'])
                                    x['value'] = value[0]
                                    pref = self._prefixes[x['prefix']][0] + str(self._prefixes[x['prefix']][1]) # [0] gives the prefix, and [1] its count.
                                    x['prefix_entity'] = f"{pref}:{helpers.escapeCharacters(x['value'])}"
                            elif x.get('xml:lang'):
                                x['value'] = re.sub(r"(['])", r"\\\1", x['value'])
                                x['prefix_entity'] = f"'{x['value']}'@{x['xml:lang']}"
                            elif x.get('datatype'):
                                x['prefix_entity'] = f"'{x['uri']}'^^<{x['datatype']}>"
                            else:
                                x['prefix_entity'] = f"'{x['value']}'"
                            
                            self.memory[x['uri']] = x # update memory
                    output.append(spo)
        
        return output

