import random

class RandomBot:
    """
    The class representing the questioner bot Randombot. 
    This bot does not rely on the state and asks random questions from the KG. 
    The answer given by the answerer (whether it is yes or no) is not incorporated at all in the next question from the KG.
    It is however saved in the history of asked questions. 

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
    """
    _name = 'Random Bot'

    def __init__(self, state, depth=20):
        self.state = state
        self.depth = depth
        self.history = []

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
            return False
        triple = random.choice(questions)
        self.history.append(triple)
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
        g = self.state.graph
        return g

    def update(self, answer):
        """
        random bot that doesn't rely on the state.
        self.state.updateGraph Is the basic approach of updating the state.
        Any other approaches, can be appended here in this method.
        """
        pass






