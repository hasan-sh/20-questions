import collections
from util import helpers

class EntropyBot:
    """

"""
    _name = 'Entropy Bot'
    initializeState = False

    def __init__(self, state, split = 0.5, depth=20):
        """
        :param int depth: 
        """
        self.state = state
        self.split = split
        self.depth = depth
        self.history = []


    def nextQuestion(self):
        # graph = helpers.rescursiveQuery(self.history, self.state.api, self.split)
        # if not graph:
        #     return False
        # triple = self.bestQuestion(graph)
        triple = helpers.rescursiveQuery(self.state, self.split)
        self.history.append(triple)
        return triple

    def update(self, answer):
        pass
        # self.state.updateGraph(self.history[-1], answer)

                                                              