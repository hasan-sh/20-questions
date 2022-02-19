import random
from util import helpers

"""
TODO: Document
- 
"""
class RandomBot:
    _name = 'Random Bot'

    def __init__(self, state, depth=20):
        self.state = state
        self.depth = depth
        self.history = []


    def nextQuestion(self):
        questions = self.getQuestions()
        triple = random.choice(questions)
        self.history.append(triple)
        triple = helpers.parseTriple(triple)
        (_, p, o) = triple
        return p + ' ' + o
        # r = random.random()
        # if r <= 0.33:
        #     return p
        # elif r > 0.33 and r <= 0.66:
        #     return p + ' ' + o
        # else:
        #     return o

    # TODO: what happens if g is empty?
    def getQuestions(self):
        # all entities in state
        g = list(self.state.graph[::])
        # select possible properties
        return g


    def update(self, answer):
        # dummy bot that doesn't rely on the state.
        # self.state.updateGraph Is the basic approach of updating the state.
        # Any other approaches, can be appended here in this method.
        pass






