import collections
from util import helpers
import random


class CorruptedEntropyBot:
    """
    TODO documentation
    """
    _name = 'Corrupted Entropy Bot'

    def __init__(self, state, corruptedKG, split = 0.5, depth=20):
        self.state = state
        self.split = split
        self.depth = depth
        self.history = []
        self.answer = 'Yes'
        self.corruptedKG = corruptedKG
        self.duplicates = []


    def nextQuestion(self):
        """
        TODO documentation
        """
        self.split = random.choice([0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 0.2, 0.3, 0.3, 0.3, 0.4, 0.4, 0.5, 0.6, 0.6, 0.7, 0.7, 0.7, 0.8, 0.8, 0.8, 0.8, 0.9, 0.9, 0.9, 0.9, 0.9])

        noise = random.random()
        noiseLevel = 0.7

        if not len(self.duplicates) or noise > noiseLevel:
            triple = helpers.rescursiveQueryX(self.state, self.corruptedKG, self.split, lastKnownAnswer = self.answer)
        else:
            questions = self.corruptedKG
            listOfQuestions = []
            for s,p,o in questions:
                s = self.state.api.memory[s[:]]
                p = self.state.api.memory[p[:]]
                o = self.state.api.memory[o[:]]
                q = s,p,o
                listOfQuestions.append(q)
            triple = random.choice(listOfQuestions)
            while helpers.parseTriple(triple)[1] == 'label' and random.random() < 0.3:
                triple = random.choice(listOfQuestions)

        if triple:
            if triple[2].get('value') in self.duplicates:
                return self.nextQuestion()
            self.duplicates.append(triple[2].get('value'))

        
        if noise > noiseLevel:
            self.state.history.append(triple)
            self.history.append(triple)

        return triple

    def update(self, answer): 
        """
        TODO documentation
        """
        self.answer = answer
        # self.state.updateGraph(self.history[-1], answer)

                                                              