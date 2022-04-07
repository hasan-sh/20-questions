import random

class BaseBot:
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
    _name = 'Base Bot'

    def __init__(self, state, depth=20):
        """
        :param int depth: for now not used, meant to include the number of allowed questions within the strategy of the bot
            TODO include this in the strategy
        """
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
            print('NO questions', questions, self.state.graph)
            return False
        questions = [q for q in questions if q]
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
        graph = self.state.graph
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
        self.state.updateGraph(self.history[-1], answer)

