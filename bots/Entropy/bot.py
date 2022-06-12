import collections
from util import helpers

class EntropyBot:
    """
    TODO documentation
    """
    _name = 'Entropy Bot'

    def __init__(self, state, split = 0.5, depth=20):
        self.state = state
        self.split = split
        self.depth = depth
        self.history = []
        self.answer = 'Yes'

    def nextQuestion(self):
        """
        TODO documentation
        """
        # graph = helpers.rescursiveQuery(self.history, self.state.api, self.split)
        # if not graph:
        #     return False
        # triple = self.bestQuestion(graph)
        triple = helpers.rescursiveQuery(self.state, self.split, lastKnownAnswer = self.answer)
        self.history.append(triple)
        return triple

    def update(self, answer): 
        """
        TODO documentation
        """
        self.answer = answer
        # self.state.updateGraph(self.history[-1], answer)

                                                              