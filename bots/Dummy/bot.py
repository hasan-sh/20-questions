import random
from util import helpers, constants

"""
Dummy bot that does not rely on the state. This bot asks random questions from the KG.
The answer (whether yes or no) is not incorporated at all in the next question nor removed from the KG.
It is however saved in the history of asked questions.

"""
class DummyBot:
    _name = 'Dummy Bot'

    def __init__(self, state, questioner=True, depth=20):
        self.state = state
        self.depth = depth
        self.history = []


    def nextQuestion(self):
        questions = self.getQuestions()
        if not questions:
            return False
        triple = random.choice(questions)
        self.history.append(triple)
        return triple

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






