import random


"""
TODO: Document
"""
class RandomBot:
    _name = 'Random Bot'

    def __init__(self, state, depth=20):
        self.state = state
        self.depth = depth
        self.history = []


    def nextQuestion(self, state):
        questions = self.getQuestions(state)
        triple = random.choice(questions)
        self.history.append(triple)
        (_, p, o) = triple
        return p + ' ' + o

    def getQuestions(self, state):
        # all entities in state
        g = state.graph
        # select possible properties
        return g








