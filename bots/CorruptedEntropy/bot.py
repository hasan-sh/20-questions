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
        # graph = helpers.rescursiveQuery(self.history, self.state.api, self.split)
        # if not graph:
        #     return False
        # triple = self.bestQuestion(graph)
        
        # self.split = random.choice([0.1, 0.1, 0.15, 0.15, 0.1, 0.1, 0.15, 0.15, 0.2, 0.2, 0.3, 0.4, 0.5, 0.7, 0.9])
        # self.split = round(random.uniform(0.10, 1.00), 2)

        
        # self.split = random.choice([0.1, 0.9])
        # print('SPLIT NOW: ', self.split)
        # if self.number % 2 == 0:
        noise = random.random()
        noiseLevel = 0.7

        if not len(self.duplicates) or noise > noiseLevel:
            # print('entropy ques')
            # print(self.history)
            # self.split = random.choice([0.1, 0.9])
            triple = helpers.rescursiveQueryX(self.state, self.corruptedKG, self.split, lastKnownAnswer = self.answer)
            # print(self.state.history, triple)
        else:
            # print('give random')
            # triple = random.choice(self.corruptedKG)
            questions = self.corruptedKG
            #  remove state.yesAnswers or no.answers from curruptedKG.
            listOfQuestions = []
            for s,p,o in questions:
                s = self.state.api.memory[s[:]]
                p = self.state.api.memory[p[:]]
                o = self.state.api.memory[o[:]]
                q = s,p,o
                listOfQuestions.append(q)
            triple = random.choice(listOfQuestions)
            while helpers.parseTriple(triple)[1] == 'labeel' and random.random() < 0.3:
                triple = random.choice(listOfQuestions)

        if triple[2].get('value') in self.duplicates:
            # print('dups dups')
            # print('dups', self.duplicates)
            return self.nextQuestion()
        
        if noise > noiseLevel:
            self.state.history.append(triple)
            self.history.append(triple)

        self.duplicates.append(triple[2].get('value'))

        return triple

    def update(self, answer): 
        """
        TODO documentation
        """
        self.answer = answer
        # self.state.updateGraph(self.history[-1], answer)

                                                              