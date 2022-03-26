import random


class BaseBot:
    """
Base bot: This bot asks random questions from the KG. 
If answer is yes:
    1- A sparql query is constructed from the triple used to ask the question. All instances where the subject appears either as
       subject or object (in the previous KG) are retrieved (through a UNION) and a new sub-KG is constructed from them.
    2- the triple itself is removed along with all triples where the predicate and object matches. 
If answer is no:
    1- the triple itself is removed along with all triples where the predicate and object matches. 
In addition all questions' triples are saved to history.s
"""
    _name = 'Base Bot'

    def __init__(self, state, depth=20):
        """
        :param int depth: bllalaib
        """
        self.state = state
        self.depth = depth
        self.history = []


    def nextQuestion(self):
        questions = self.getQuestions()
        if not questions:
            print('NO questions', questions, self.state.graph)
            return False
        questions = [q for q in questions if q]
        triple = random.choice(questions)
        # getRandom = lambda: random.choice(questions)
        # triple = getRandom()
        # while not triple:
        #     print("NO CHOICE, generate another triple!")
        #     triple = getRandom()
        #     print('Chose: ', triple)
        self.history.append(triple)
        return triple

    # TODO: what happens if g is empty?
    def getQuestions(self):
        # return self.rescursive_query(self.state.yesHints[-1][1]['value'], 
        #     self.state.yesHints[-1][2]['value'])
        
        # all entities in state
        graph = self.state.graph
        # select possible properties
        return graph

    def update(self, answer):
        self.state.updateGraph(self.history[-1], answer)

