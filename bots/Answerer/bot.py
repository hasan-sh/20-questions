from tkinter.messagebox import YES
from util import helpers, api, constants
import random
class Answerer:
    def __init__(self, ignoranceLevel = 0) -> None:
        self.ignoranceLevel = ignoranceLevel
        # The answerer thinks of an entity.
        self.api = api.API()
        self.entity = self.pickEntity()
        while not self.entity:
            self.entity = self.pickEntity()
        result = self.collectTriples(self.entity)
        # print('the result ', result)        
        self.entityTriples = [[row['uri'] for row in rows] for rows in result]
        # self.entityTriples = self.collectTriples(self.entity)
        print('CHOSEN ENTITY: ', self.entity, '\n')

    def collectTriples(self, entity):
        """
        Gathers all triples that give information about the chosen entity.
        """
        
        query ="""
              select *
              where {
                <%s> ?p ?o .
              }
        """%(entity[0]['uri'])
        qres = self.api.queryKG(query)
        qres = self.api.parseJSON(qres, [['p','o']])
        return qres



    def getAnswer(self, question):
        """
        Fetches the answer to the question about the entity posed by the questioner,
        by seeing if the chosen entity has a triple with po.

        Example: questionner("type human?")
                 answerer(does "type human" hold?)
        """
        _, p, o = question
        # print('the entities', self.entityTriples)
        # print([p['uri'], o['uri']])
        # input('sexy me!')
        if [p['uri'], o['uri']] in self.entityTriples:
            return 'yes'
        else:
            return 'no'
    
    def pickEntity(self):
        #  we pick something that has some label
        query ="""
        SELECT distinct ?s
            WHERE {
                ?s <http://www.w3.org/2000/01/rdf-schema#label> ?__.
            }
        """
        g = self.api.queryKG(query)
        g = self.api.parseJSON(g, [['s']])
        entity = random.choice(g)
        return entity
        