import random
from util import helpers
import rdflib
from rdflib import URIRef

class CorruptedBaseBot:
    """
    The class representing the questioner bot Basebot. 
    This bot asks random questions from the KG. 
    If answer is yes:
        1- A sparql query is constructed from the triple used to ask the question. All instances where the subject appears as
        subject (in the previous KG) are retrieved and a new sub-KG is constructed from them.
        2- the triple itself is removed along with all triples where the predicate and object matches. 
    If answer is no:
        1- All entities where the predicate object combination holds are filtered out. 
    In addition all questions' triples are saved to history.s

    Attributes
    ----------
    state : Class
        Contains all the informations about the current game state. 
    depth : int
        idk how to describe this ;-; --Help (default is 20) TODO
    _name : str
        The name of the bot.

    Methods
    -------
    nextQuestion()
        Picks a question to pose to the Answerer.
    
    getQuestions()
        Fetches the current graph.
    
    update(answer)
        Updates game state with the question and the provided answer. 
        Calls state.updateGraph()
    """
    _name = 'Corrupted Base Bot'

    def __init__(self, state, corruptedKG, depth=20):
        """
        :param int depth: for now not used, meant to include the number of allowed questions within the strategy of the bot
            TODO include this in the strategy
        """
        self.state = state
        self.depth = depth
        self.history = []
        self.corruptedKG = corruptedKG

    def nextQuestion(self):
        """
        Picks a question to pose to the Answerer.

        Parameters -> None

        Returns
        -------
        triple
            A randomly selected triple from the current knowledge graph.
        """
        questions = self.getQuestions()
        if not questions:
            # print('NO questions', questions)
            return False
        listOfQuestions = []
        for s,p,o in questions:
            s = self.state.api.memory[s[:]]
            p = self.state.api.memory[p[:]]
            o = self.state.api.memory[o[:]]
            q = s,p,o
            listOfQuestions.append(q)
        # questions = [q for q in questions if q]
        triple = random.choice(listOfQuestions)
        
        self.history.append(triple)
        # print('Asked Question:', helpers.parseTriple(triple))
        return triple   

    def getQuestions(self):
        """
        Fetches the current graph.
        
        Parameters -> None

        Returns
        -------
        graph
            The current game's graph.
        """
        graph = self.corruptedKG
        return graph

    def update(self, answer):
        """
        Updates the current game's graph by using the answerer's answer along with the question asked.
        
        Parameters
        ----------
        answer : str
            A 'yes' or 'no' answer given by the answerer.

        Returns -> None
        """
        # pass
        # if (URIRef("http://yago-knowledge.org/resource/Joe_Biden"), None, None) in self.corruptedKG:
        #         print("before, blabla in base")


        self.corruptedKG = self.state.createSubGraphX(answer, self.corruptedKG)


        # if (URIRef("http://yago-knowledge.org/resource/Joe_Biden"), None, None) in self.corruptedKG:
        #         print("after, blabla in base")

