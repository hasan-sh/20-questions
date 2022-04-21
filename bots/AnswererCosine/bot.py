from tkinter.messagebox import YES

from SPARQLWrapper import QueryResult
from util import helpers, api, constants
import random
import numpy as np

class AnswererCosine:
    """
    The Class representing the Answerer in case there is no human player.
    
    Attributes
    ----------
    ignoranceLevel : int
        a number from 0 - 100 representing how much this bot knows about the chosen entity.
        0 --> Answerer bot knows everything about the entity that it can find in the KG.
        50 --> There's 50% chance that the answer could be picked randomly. 
        100 --> Answerer bot knows nothing about the entity. Answer would be picked randomly.

    mode: str
        easy --> returns RANDOM answers according to the chance provided by the ignorance level 
        hard --> returns WRONG answers according to the chance provided by the ignorance level
        
    Methods
    -------
    collectTriples(entity)
        Gathers all the triples from the KG about the chosen entity.
        
    getAnswer(question)
        Using the question posed by a questioner bot, finds whether the chosen entity has a certain property.
        Returns yes if it can find a triple that confirms that the chosen entity has the property from the 
        question, else returns no.
        
    pickEntity()
        Queries the KG to randomly select an entity that has both a type and a label. 
        This chosen entity will be used to answer the questions posed by the questioner bot.
    """

    def __init__(self, ignoranceLevel = 0, mode = 'easy'):
        self.ignoranceLevel = ignoranceLevel
        self.api = api.API()
        self.entity = self.pickEntity()
        # self.entity = [{
        #   "type": "uri",
        #   "uri": "http://yago-knowledge.org/resource/Taylor_Swift"
        #   "uri": "http://yago-knowledge.org/resource/Borussia_Dortmund"
        # }]
        while not self.entity:
            self.entity = self.pickEntity()
        result = self.collectTriples(self.entity)
        self.entityTriples = [[row.get('uri') for row in rows] for rows in result]
        self.mode = mode
        print('CHOSEN ENTITY: ', self.entity, '\n')
        print('Number of entityTriples', len(self.entityTriples))

    def predicateCount(self):
        query = """SELECT ?p (COUNT (?p) as ?predicates)
                    WHERE { ?s ?p ?o.}
                    GROUP BY ?p"""
        qres = self.api.queryKG(query)
        result = []
        for i in qres['results']['bindings']:
            result.append([i['p']['value'], i['predicates']['value']])
        return result

    def collectTriples(self, entity):
        """
        Gathers all the triples from the KG about the chosen entity.

        Parameters
        ----------
        entity : str
            The entity selected from the KG.

        Returns
        -------
        qres
           A list of predicate object pairs where the chosen entity is in the subject position. 
        """
        
        query ="""
              select *
              where {
                <%s> ?p ?o .
              }
        """%(entity[0].get('uri'))
        qres = self.api.queryKG(query)
        qres = self.api.parseJSON(qres, [['p','o']])
        return qres

    def collectPredicates(self, entity):
        query ="""
              select ?p
              where {
                <%s> ?p ?o .
              }
        """%(entity[0].get('uri'))
        qres = self.api.queryKG(query)
        qres = self.api.parseJSON(qres, [['p']])
        predicates = []
        for i in qres:
            for j in i:
                predicates.append(j.get('uri'))
        return predicates

    def collectEntities(self):
        query = """SELECT DISTINCT ?s
                WHERE{
                    ?s a ?_.
                    ?s <http://www.w3.org/2000/01/rdf-schema#label> ?__.
                    ?s ?p ?o. """
        qentity = self.api.queryKG(query)
        return qentity

    def getAnswer(self, question):
        """
        Finds the answer to the question posed by the questioner bot.
        
        Parameters
        ----------
        question : str
            The triple given by the questioner bot.
            
        Returns
        -------
        'yes' 
            if the predicate/object combination is found in the list of triples about the chosen entity.
        'no'
            if the predicate/object combination is not found in the list of triples about the chosen entity.
        
        Example: questionner("type human?")
                 answerer(does "type human" hold?)
        """
        _, p, o = question
        if [p.get('uri'), o.get('uri')] in self.entityTriples:
            return 'yes'
        else:
            return 'no'
    
    def collectEntities(self):
        query = """ SELECT DISTINCT ?s 
                    WHERE {
                        ?s a ?_.
                        ?s <http://www.w3.org/2000/01/rdf-schema#label> ?__.
                        ?s ?p ?o.
                    }"""
        g = self.api.queryKG(query)
        g = self.api.parseJSON(g, [['s']])
        return g

    def comparison(self):
        amountPredicates = self.predicateCount()
        outliers = []
        ent = self.collectEntities()
        for i in ent:
            simscore = 0
            compList = [x for y, x in enumerate(ent) if y!=ent.index(i)]
            targetTriples = self.collectPredicates(i)
            targetVector = helpers.createVector(targetTriples, amountPredicates)
            # Catching the exception generated     
            for j in compList:
                compTriples = self.collectPredicates(j)
                compVector = helpers.createVector(compTriples, amountPredicates)
                simscore += helpers.cosineSimilarity(targetVector, compVector)
            print(i, simscore)
            if (simscore/len(compList)) < 0.1:
                outliers.append(i)
        print(outliers)
        return outliers


    def pickEntity(self):
        g = self.comparison()
        entity = random.choice(g)
        return entity