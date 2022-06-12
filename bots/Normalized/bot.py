from util import helpers
import numpy as np
from collections import Counter
import random

class NormalizedABot:
    _name = 'Normalized Bot'

    def __init__(self, state):
        self.api = state.api
        self.state = state
        self.countIndex = {}
        self.SSI = {} # SmartScoreIndex
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
        highest = max(self.SSI.values())
        indices = [i for i, j in enumerate(self.SSI.values()) if j == highest]
        best = list(self.SSI.keys())[random.choice(indices)]
        return helpers.keyToQuestion(best, self.api)

    def updateScore(self, question = None, answer = None):
        '''
        Count and Score Index are created upon intilization. Score is initialized to be the normalized counts.
        Count index is then not used anymore.
        Score index is then updated each question with *100(yes) and *0.01(no) OR +1 and -1'''
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
                    self.SSI[res] *= self.inforce if answer == 'yes' else self.punish
                except: pass
            
            #  delete the entry of the asked question (to no ask it anymore)
            self.SSI.pop( str(question[1]['uri'] + '()()' + question[2]['uri']) )

        else: # means we just started => intialize score
            for res in results:
                try: self.countIndex[res] += 1 # count
                except: self.countIndex[res] = 1 # else initialize
            ''' SSI will contain the normalized counts /scores ,
                countIndex will store the  counts'''

            # normalize the values in our index
            factor = 1.0/sum(self.countIndex.values())
            self.SSI = {key:value*factor for key,value in self.countIndex.items()}
