import random


class BaseBot:
    """
    The class representing the questioner bot Basebot. 
    This bot asks random questions from the KG. 
    If answer is yes:
        1- A sparql query is constructed from the triple used to ask the question. All instances where the subject appears either as
        subject or object (in the previous KG) are retrieved (through a UNION) and a new sub-KG is constructed from them.
        2- the triple itself is removed along with all triples where the predicate and object matches. 
    If answer is no:
        1- the triple itself is removed along with all triples where the predicate and object matches. 
    In addition all questions' triples are saved to history.s

    Attributes
    ----------
    state : Class??
        Contains all the informations about the current game state.
    depth : int
        idk how to describe this ;-; --Help (default is 20)
    _name : str
        The name of the bot.

    Methods
    -------
    nextQuestion()
        Picks a question to pose to the Answerer.
    
    getQuestions()
        Fetches the current graph.
    
    recursive_query(p, o, depth = 0)
        Queries the KG to find all unique predicate/object combinations? --Help

    update(answer)
        Updates game state using the answer given by the answerer. 

"""
    _name = 'Base Bot'

    def __init__(self, state, depth=20):
        """
        Parameters
        ----------
        state : Class??
            The initial game state.
        depth : int
            idk how to describe this ;-; --Help (default is 20)
        """
        self.state = state
        self.depth = depth
        self.history = []


    def nextQuestion(self):
        """Picks a question to pose to the Answerer.

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

    # TODO: what happens if g is empty?
    def getQuestions(self):
        """Fetches the current graph.
        
        Returns
        -------
        graph
            The current game's graph.
        """
        # return self.rescursive_query(self.state.yesHints[-1][1]['value'], 
        #     self.state.yesHints[-1][2]['value'])
        
        # all entities in state
        graph = self.state.graph
        # select possible properties
        return graph

    def rescursive_query(self, p, o, depth=0):
        """I need help with this one
        """
        query = f"""
        SELECT distinct {p} {o} 
                (count(concat(str({p}), str({o}))) as ?poCount)
        WHERE {{
        ?s {p} {o}.
        }}
        GROUP BY {p} {o}
        ORDER BY DESC (?poCount )
        limit 10000
        """
        # make query
        # select result
        qres = self.state.api.queryKG(query=query)
        qres = self.state.api.parseJSON(qres, ["s"])
        result = qres[0]
        if depth > 0:
            return self.rescursive_query(result[0]['value'], result[1]['value'], depth-1)
        return result


    def update(self, answer):
        """Updates the current game's graph by using the answerer's answer.
        
        Parameters
        ----------
        answer : str
            A 'yes' or 'no' answer given by the answerer.
        """
        self.state.updateGraph(self.history[-1], answer)

