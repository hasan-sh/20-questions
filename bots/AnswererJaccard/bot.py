from tkinter.messagebox import YES
from util import helpers, api, constants
import random
import numpy as np

class AnswererJaccard:
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
        self.index = {}
        self.ent = self.collectEntities()
        self.amountPredicates = self.predicateCount()
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
        qres = self.api.parseJSON(qres,  [['p','predicates']])
        result = []
        # for i in qres['results']['bindings']:
        #     result.append([i['p']['value'], i['predicates']['value']])
        for i in qres:
            result.append([i[0]['uri'], i[1]['uri']])
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
        """%(entity)
        qres = self.api.queryKG(query)
        qres = self.api.parseJSON(qres, [['p','o']])
        return qres

    def collectPredicates(self, entity):
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
                    }
                """
        g = self.api.queryKG(query)
        g = self.api.parseJSON(g, [['s']])
        return g

    def createIndex(self):
        query = """ select ?s ?p (count(?p) as ?pCount) where { 
                    	?s ?p ?o .
                    } group by ?s ?p
                    """
        g = self.api.queryKG(query)
        g = self.api.parseJSON(g, [['s', 'p', 'pCount']])
        # results = [str(res[0]['uri']) for res in g]
        g = [res for res in g if res]
        for res in g:
            # print(res[0])
            if str(res[0]['uri']) in self.index.keys():
                # self.index[str(res[0]['uri'])] = { 'predicates' : str(res[1]['uri']) 
                self.index[str(res[0]['uri'])]['predicates'].append(str(res[1]['uri']) )
                self.index[str(res[0]['uri'])]['counts'].append(str(res[2]['uri']) )
            else:
                self.index[str(res[0]['uri'])] = {'predicates' : [str(res[1]['uri']) ], 'counts': [str(res[2]['uri']) ]}

    def comparison(self):
        outliers = []
        self.createIndex() # make an index that connects entries (subjects) ==> predicates
        for i in self.ent:
            simscore = 0
            compList = [x for y, x in enumerate(self.ent) if y!=self.ent.index(i)]
            # targetTriples = self.collectPredicates(i) # self.index[i] => predicates
            targetTriples = self.index[i[0]['uri']]['predicates']
            # Catching the exception generated     
            for j in compList:
                # compTriples = self.collectPredicates(j)
                compTriples = self.index[j[0]['uri']]['predicates']
                simscore += helpers.jaccard(targetTriples, compTriples)
            print(i, simscore)
            if (simscore/len(compList)) < 0.1:
                outliers.append(i)
        print(outliers)
        return outliers


    def pickEntity(self):
        g = self.comparison()
        entity = random.choice(g)
        return entity
        