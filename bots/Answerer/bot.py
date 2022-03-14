from tkinter.messagebox import YES
from util import helpers, api, constants
import random
class Answerer:
    def __init__(self, ignoranceLevel = 0) -> None:
        self.ignoranceLevel = ignoranceLevel
        # The answerer thinks of an entity.
        self.api = api.API()
        self.entity = self.pickEntity()
        self.entityTriples = self.collectTriples(self.entity)
        # print('CHOSEN ENTITY: ', self.entity)

    def collectTriples(self, entity):
        query ="""
            select *
            where {
                {<%s> ?p ?o .}
                UNION
                {?s1 ?p1 <%s> .}
            }
        """%(entity[0]['value'], entity[0]['value'])
        qres = self.api.queryKG(query)  
        qres = self.api.parseJSON(qres, [['p','o'], ['p1','s1']])
        return qres


    def getAnswer(self, question):
        """
        Example: questionner("type human?")
                 answerer(does "type human" hold?)
        """
        _, p, o = question
        if [p['value'], o['value']] in self.entityTriples:
            return 'yes'
        else:
            return 'no'
    
    def pickEntity(self):
        # we pick something that has some type # some discussing needed#########
        query ="""
        SELECT distinct ?s
            WHERE {

                ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?_.
                ?s <http://www.w3.org/2000/01/rdf-schema#label> ?__.
            }
        """
        g = self.api.queryKG(query)
        g = self.api.parseJSON(g, ['s'])
        entity = random.choice(g)
        return entity
        