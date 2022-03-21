import collections

class EntropyBot:
    """

"""
    _name = 'Entropy Bot'

    def __init__(self, state, split = 0.5, depth=20):
        """
        :param int depth: 
        """
        self.state = state
        self.split = split
        self.depth = depth
        self.history = []


    def nextQuestion(self):
        graph = self.state.graph
        if not graph:
            return False
        triple = self.bestQuestion(graph)
        self.history.append(triple)
        return triple
    
    # Calculates information gain over all questions and returns best question 
    def bestQuestion(self, graph):
        candidates = collections.Counter((triple[1]['value'], triple[2]['value'])  for triple in graph)

        totalTriples = len(candidates) 

        return min(candidates.items(), key=lambda x: abs(x[1] - totalTriples * self.split))
                                                              