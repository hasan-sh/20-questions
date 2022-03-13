from tkinter.messagebox import YES
import rdflib
from util import helpers, api, constants
import random
class Answerer:
    def __init__(self, ignoranceLevel = 0) -> None:
        self.ignoranceLevel = ignoranceLevel
        # The answerer thinks of an entity.
        self.api = api.API()
        # self.graph = graph # this stays the same throughout the game
        self.entity = self.pickEntity()

        print('CHOSEN ENTITY: ', helpers.parseTriple(self.entity))

    def getAnswer(self, question):
        # print(question)
        """
        Example: questionner("type human?")
                 answerer(does "type human" hold?)
        """
        
        query ="""
        SELECT ?s
        WHERE {
            ?s <%s> <%s> .
        }
        """%(question[1], question[2])
        if question[1] in constants.literalPredicates:
            query ="""
        SELECT ?s
        WHERE {
            ?s <%s> "%s" .
        }
        """%(question[1], question[2])
        # qres = self.graph.query(query)
        qres = self.api.queryKG(query)
        qres = self.api.parseJSON(qres,['s'])
        for t in qres:
            # if self.entity[0] == t.s:
            if self.entity[0] == t[0]:
                return 'yes'
        return 'no'
    
    def pickEntity(self):
        # g = list(self.graph[::])
        # g = self.state.graph

        # we pick something that has some type
        query ="""
        SELECT ?s ?p ?o
        WHERE {
            
            ?s a ?o. BIND('http://www.w3.org/1999/02/22-rdf-syntax-ns#type' AS ?p)
        }
        """
        # ?s a ?o .  BIND('http://www.w3.org/2000/01/rdf-schema#label' AS ?p)
        g = self.api.queryKG(query)
        g = self.api.parseJSON(g)
        triple = random.choice(g)
        return triple
        