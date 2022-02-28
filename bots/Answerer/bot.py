from tkinter.messagebox import YES
import rdflib
from util import helpers
import random
class Answerer:
    def __init__(self, graph, ignoranceLevel = 0) -> None:
        self.ignoranceLevel = ignoranceLevel
        # The answerer thinks of an entity.
        self.graph = graph # this stays the same throughout the game
        self.entity = self.pickEntity(self.graph)
        print('CHOSEN ENTITY: ', helpers.parseTriple(self.entity))

    def getAnswer(self, question):
        """
        Example: questionner("type human?")
                 answerer(does "type human" hold?)
        """
        query ="""
        SELECT ?s
        WHERE {
            ?s <%s> <%s> .
        }
        """%(question[1], question[2].replace(' ', '_'))
        
        qres = self.graph.query(query)
        for t in qres:
            if self.entity[0] == t.s:
                return 'yes'
        return 'no'
    
    def pickEntity(self, g):
        g = list(self.graph[::])
        triple = random.choice(g)
        return triple
        