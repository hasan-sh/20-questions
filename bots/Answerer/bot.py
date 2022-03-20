from tkinter.messagebox import YES
from util import helpers, api, constants
import random
class Answerer:
    """
    The Class representing the Answerer in case there is no human player.
    
    Attributes
    ----------
    ignoranceLevel : int
        a number from 0 - 100 representing how much this bot knows about the chosen entity.
        0 --> Answerer bot knows everything about the entity that it can find in the KG.
        100 --> Answerer bot knows nothing about the entity.
        
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

    def __init__(self, ignoranceLevel = 0) -> None:
        """
        Parameters
        ----------
        ignoranceLevel : int
        a number from 0 - 100 representing how much this bot knows about the chosen entity (default is 0).
        0 --> Answerer bot knows everything about the entity that it can find in the KG.
        100 --> Answerer bot knows nothing about the entity.
        """
        self.ignoranceLevel = ignoranceLevel
        # The answerer thinks of an entity.
        self.api = api.API()
        self.entity = self.pickEntity()
        self.entityTriples = self.collectTriples(self.entity)
        # print('CHOSEN ENTITY: ', self.entity)

    def collectTriples(self, entity):
        """Gathers all the triples from the KG about the chosen entity.

        Parameters
        ----------
        entity : str
            The entity selected from the KG.

        Returns
        -------
        qres
           A list of triples with the chosen entity in the subject position. 
        """
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
        """Finds the answer to the question posed by the questioner bot.
        
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
        """
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
        """Queries the KG to randomly select an entity with a type and a label.

        Returns
        -------
        entity
            the URI of the entity selected by the Answerer bot. 
        """
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
        