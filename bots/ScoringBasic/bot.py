from util import helpers
import numpy as np
from collections import Counter
import random

class ScoringBasicBot:
    _name = 'ScoringBasic Bot'

    def __init__(self, state):
        self.api = state.api
        self.state = state
        self.scoreIndex = {}
        self.history = []
        self.inforce = 1
        self.punish = -1
        self.updateScore()
        
    def nextQuestion(self):
        triple = self.bestQuestion()
        self.history.append(triple)
        return triple

    def update(self, answer): 
        self.updateScore(question=self.history[-1],answer=answer)

    def bestQuestion(self):
        ''' DOWN makes use of only score '''
        highest = max(self.scoreIndex.values())
        indices = [i for i, j in enumerate(self.scoreIndex.values()) if j == highest]
        best = list(self.scoreIndex.keys())[random.choice(indices)]

        # best = list(self.scoreIndex.keys())[list(self.scoreIndex.values()).index(highest)]
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
                    self.scoreIndex[res] += self.inforce if answer == 'yes' else -self.punish
                except: pass
            
            print(self.scoreIndex['http://www.w3.org/2000/01/rdf-schema#label()()Taylor Swift'])
            print(list(self.scoreIndex.keys())[list(self.scoreIndex.values()).index(max(self.scoreIndex.values()))], max(self.scoreIndex.values()))

            # delete the entry of the asked question (to no ask it anymore)
            self.scoreIndex.pop( str(question[1]['uri'] + '()()' + question[2]['uri']) )

        else: # means we just started => intialize score
            for res in results:
                if res not in self.scoreIndex.keys():
                    self.scoreIndex[res] = 1 # else initialize
            ''' scoreIndex will contain the scores'''

        # print(list(self.scoreIndex.keys())[list(self.scoreIndex.values()).index(max(self.scoreIndex.values()))], \
        #     'which occurs for ', list(self.scoreIndex.values()).count(max(self.scoreIndex.values())))

