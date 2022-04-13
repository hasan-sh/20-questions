from util import helpers
import numpy as np
from collections import Counter
import random

class ScoringEntropyBot:
    _name = 'ScoringEntropy Bot'

    def __init__(self, state, split=0.5):
        self.api = state.api
        self.state = state
        self.split = split
        self.answer = 'Yes'
        self.scoreIndex = {}
        self.countIndex = {}
        self.history = []
        self.inforce = +1
        self.punish = -1
        self.updateScore()
        self.switch = False
        
    def nextQuestion(self):
        # if not self.switch:
        #     triple = helpers.rescursiveQuery(self.state, self.split, lastKnownAnswer = self.answer)
        #     if triple:
        #         self.history.append(triple)
        #         return triple
        #     else:
        #         self.switch = True    
        #         print('Now using scores')
        #         return self.nextQuestion()
        # else:
            triple = self.bestQuestion()
            self.history.append(triple)
            return triple

    def update(self, answer): 
        self.answer = answer
        self.updateScore(question=self.history[-1],answer=answer)

    def bestQuestion(self):
        ''' DOWN makes use of only score '''

        # highest = max(self.scoreIndex.values())
        # indices = [i for i, j in enumerate(self.scoreIndex.values()) if j == highest]
        # if len(indices) > 1: 
        #     best = list(self.scoreIndex.keys())[random.choice(indices)]
        # else:
        #     best = list(self.scoreIndex.keys())[indices[0]]

        # best = list(self.scoreIndex.keys())[list(self.scoreIndex.values()).index(highest)]

        # totalCount = sum(self.countIndex.values())
        # best = min(self.countIndex, key=lambda x: abs(int(self.countIndex[x]) - int(totalCount) * self.split))
        totalCount = sum(self.scoreIndex.values())
        best = min(self.scoreIndex, key=lambda x: abs(int(self.scoreIndex[x]) - int(totalCount) * self.split))

        return helpers.keyToQuestion(best, self.api)

    def updateScore(self, question = None, answer = None):
        prefixes = '\n'.join(self.api.prefixes)
        query = f"""
            {prefixes}
            select ?p ?o 
            where {{?s ?p ?o; 
                {" {} {}".format(question[1]['prefix_entity'], question[2]['prefix_entity'])} .
                       }}
            GROUP BY ?p ?o
            """ if answer else """
            select ?p ?o
            where { ?s ?p ?o .}
            """
        qres = self.api.queryKG(query=query)
        qres = self.api.parseJSON(qres, [[ 'p', 'o']])
        results = [str(res[0]['uri'] + '()()' + res[1]['uri']) for res in qres]
        
        if answer:
            for res in results:
                try:
                    self.scoreIndex[res] += self.inforce if answer == 'yes' else self.punish
                except: pass

            # print(self.scoreIndex['http://www.w3.org/2000/01/rdf-schema#label()()Taylor Swift'])
            # print(list(self.scoreIndex.keys())[list(self.scoreIndex.values()).index(max(self.scoreIndex.values()))], max(self.scoreIndex.values()))
            
            #  delete the entry of the asked question (to no ask it anymore)
            self.scoreIndex.pop( str(question[1]['uri'] + '()()' + question[2]['uri']) )
            self.countIndex.pop( str(question[1]['uri'] + '()()' + question[2]['uri']) )

        else: # means we just started => intialize score
            for res in results:
                try: self.countIndex[res] += 1 # count
                except: self.countIndex[res] = 1 # else initialize
            ''' scoreIndex will contain the scores,
                countIndex will store the (normalized) counts'''

            # normalize the values in our index
            factor = 1.0/sum(self.countIndex.values())
            self.scoreIndex = {key:value*factor for key,value in self.countIndex.items()}

        # print(list(self.scoreIndex.keys())[list(self.scoreIndex.values()).index(max(self.scoreIndex.values()))], \
        #     'which occurs for ', list(self.scoreIndex.values()).count(max(self.scoreIndex.values())))

