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

    def __init__(self, ignoranceLevel = 0.2, mode = 'hard'): # modes easy and hard
        self.ignoranceLevel = ignoranceLevel
        self.api = api.API()
        # self.entity = self.pickEntity()
        self.entity = [{
          "type": "uri",

        #   "uri": "http://yago-knowledge.org/resource/Grey's_Anatomy", #strong entity 237 po's
        #   "value": "Grey's Anatomy",

        #   "uri": "http://yago-knowledge.org/resource/Taylor_Swift", #33
        #   "value": "Taylor Swift",

          "uri": "http://yago-knowledge.org/resource/Robin_Williams", #51 ==> 42ish
          "value": "Robin Williams",

        #   "uri": "http://yago-knowledge.org/resource/Megan_Fox", # 14 ==> 35ish
        #   "value": "Megan Fox"

        #   "uri": "http://yago-knowledge.org/resource/Tobey_Maguire", #16 ==> 38ish
        #   "value": "Tobey",
        
        #   "uri": "http://yago-knowledge.org/resource/Emma_Stone",
        #   "value": "",
        }]
        # while not self.entity:
        #     self.entity = self.pickEntity()
        # result = self.collectTriples(self.entity)
        # self.entityTriples = [[row.get('uri') for row in rows] for rows in result]
        self.entityTriples = [['http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'http://yago-knowledge.org/resource/Human'], ['http://www.w3.org/2002/07/owl#sameAs', 'http://g.co/kg/m/0dzf_'], ['http://www.w3.org/2002/07/owl#sameAs', 'http://www.wikidata.org/entity/Q83338'], ['http://www.w3.org/2000/01/rdf-schema#label', 'Robin Williams'], ['http://schema.org/award', 'http://yago-knowledge.org/resource/Golden_Globe_Cecil_B._DeMille_Award'], ['http://schema.org/award', 'http://yago-knowledge.org/resource/Golden_Globe_Award_for_Best_Actor_–_Motion_Picture_Musical_or_Comedy'], ['http://schema.org/award', 'http://yago-knowledge.org/resource/Screen_Actors_Guild_Award_for_Outstanding_Performance_by_a_Cast_in_a_Motion_Picture'], ['http://schema.org/award', 'http://yago-knowledge.org/resource/Disney_Legends'], ['http://schema.org/award', 'http://yago-knowledge.org/resource/Grammy_Award_for_Best_Album_for_Children'], ['http://schema.org/award', 'http://yago-knowledge.org/resource/Women_in_Film_Crystal_+_Lucy_Awards'], ['http://schema.org/award', 'http://yago-knowledge.org/resource/Academy_Award_for_Best_Supporting_Actor'], ['http://schema.org/award', 'http://yago-knowledge.org/resource/National_Board_of_Review_Award_for_Best_Actor'], ['http://schema.org/award', 'http://yago-knowledge.org/resource/49th_Golden_Globe_Awards'], ['http://schema.org/award', 'http://yago-knowledge.org/resource/MTV_Movie_Award_for_Best_Comedic_Performance'], ['http://schema.org/award', 'http://yago-knowledge.org/resource/Golden_Globe_Award_for_Best_Motion_Picture_–_Musical_or_Comedy'], ['http://schema.org/award', 'http://yago-knowledge.org/resource/Screen_Actors_Guild_Award_for_Outstanding_Performance_by_a_Male_Actor_in_a_Supporting_Role'], ['http://schema.org/award', 'http://yago-knowledge.org/resource/Grammy_Award_for_Best_Comedy_Album'], ['http://schema.org/award', 'http://yago-knowledge.org/resource/62nd_Golden_Globe_Awards'], ['http://schema.org/award', 'http://yago-knowledge.org/resource/Primetime_Emmy_Award_for_Outstanding_Individual_Performance_in_a_Variety_or_Music_Program'], ['http://schema.org/award', 'http://yago-knowledge.org/resource/45th_Golden_Globe_Awards'], ['http://schema.org/award', 'http://yago-knowledge.org/resource/36th_Golden_Globe_Awards'], ['http://schema.org/award', 'http://yago-knowledge.org/resource/51st_Golden_Globe_Awards'], ['http://schema.org/alumniOf', 'http://yago-knowledge.org/resource/Juilliard_School'], ['http://schema.org/alumniOf', 'http://yago-knowledge.org/resource/Redwood_High_School_(Larkspur,_California)'], ['http://schema.org/alumniOf', 'http://yago-knowledge.org/resource/College_of_Marin'], ['http://schema.org/alumniOf', 'http://yago-knowledge.org/resource/Claremont_McKenna_College'], ['http://schema.org/alumniOf', 'http://yago-knowledge.org/resource/Detroit_Country_Day_School'], ['http://schema.org/image', 'http://commons.wikimedia.org/wiki/Special:FilePath/Robin%20Williams%202011a%20%282%29.jpg'], ['http://schema.org/spouse', 'http://yago-knowledge.org/resource/Marsha_Garces_Williams'], ['http://schema.org/spouse', 'http://yago-knowledge.org/resource/Susan_Schneider_(artist)'], ['http://schema.org/deathDate', '2014-08-11'], ['http://schema.org/nationality', 'http://yago-knowledge.org/resource/United_States'], ['http://schema.org/familyName', 'http://yago-knowledge.org/resource/Williams_(surname)'], ['http://schema.org/givenName', 'http://yago-knowledge.org/resource/Robin_(name)'], ['http://schema.org/homeLocation', 'http://yago-knowledge.org/resource/Chicago'], ['http://schema.org/homeLocation', 'http://yago-knowledge.org/resource/Paradise_Cay,_California'], ['http://schema.org/homeLocation', 'http://yago-knowledge.org/resource/San_Francisco'], ['http://schema.org/homeLocation', 'http://yago-knowledge.org/resource/Bloomfield_Hills,_Michigan'], ['http://schema.org/homeLocation', 'http://yago-knowledge.org/resource/Sea_Cliff,_San_Francisco'], ['http://schema.org/birthPlace', 'http://yago-knowledge.org/resource/Chicago'], ['http://schema.org/url', 'http://www.robinwilliams.com/'], ['http://schema.org/knowsLanguage', 'http://yago-knowledge.org/resource/English_language'], ['http://schema.org/hasOccupation', 'http://yago-knowledge.org/resource/Mime_artist'], ['http://schema.org/hasOccupation', 'http://yago-knowledge.org/resource/Comedian'], ['http://schema.org/hasOccupation', 'http://yago-knowledge.org/resource/Film_producer'], ['http://schema.org/hasOccupation', 'http://yago-knowledge.org/resource/Actor'], ['http://schema.org/hasOccupation', 'http://yago-knowledge.org/resource/Screenwriter'], ['http://schema.org/hasOccupation', 'http://yago-knowledge.org/resource/Stage_actor'], ['http://schema.org/birthDate', '1951-07-21'], ['http://schema.org/children', 'http://yago-knowledge.org/resource/Zelda_Williams'], ['http://schema.org/deathPlace', 'http://yago-knowledge.org/resource/Tiburon,_California']]
        # print(self.entityTriples)
        self.mode = mode
        print('CHOSEN ENTITY: ', helpers.parseTriple(self.entity))
        print('Number of entityTriples', len(self.entityTriples))

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
        if p['value'] not in ['label', 'image', 'givenName', 'sameAs']: # dont lie when it comes to labels
            if self.ignoranceLevel > 0:
                if random.randint(0,100) < self.ignoranceLevel*100:
                    """ Here there can be two options either a random answer or just the wrong answer"""
                    if self.mode == 'easy':
                        # print('this is random answer')
                        if random.randint(0,100)%2 == 0:
                            return 'yes'
                        else:
                            return 'no'
                    elif self.mode == 'hard':
                        # print('this is wrong answer')
                        if [p.get('uri'), o.get('uri')] in self.entityTriples:
                            return 'no'
                        else:
                            return 'yes'
        
        if [p.get('uri'), o.get('uri')] in self.entityTriples:
            return 'yes'
        else:
            return 'no'
    
    def pickEntity(self):
        """
        Queries the KG to randomly select an entity with a type and a label.

        Parameters -> None

        Returns
        -------
        entity
            The URI of the entity selected by the Answerer bot. 
        """
        query ="""
        SELECT distinct ?s
            WHERE {
                ?s a ?_.
                ?s <http://www.w3.org/2000/01/rdf-schema#label> ?__.
            }
        """
        g = self.api.queryKG(query)
        g = self.api.parseJSON(g, [['s']])
        entity = random.choice(g)
        return entity
        