from util import helpers
import numpy as np
from collections import Counter
import random

class EC1Bot:
    _name = 'EC1 Bot'

    def __init__(self, state):
        self.api = state.api
        self.state = state
        self.answer = 'Yes'
        self.scoreIndex = {}
        self.countIndex = {}
        self.combinedIndex = {}
        self.entropyIndex = {}
        self.history = []
        self.scoreWeight = 0.1
        self.entropyWeight = 0.9
        self.inforce = 1
        self.punish = -1
        self.updateScore()
        
    def nextQuestion(self):
        triple = self.bestQuestion()
        self.history.append(triple)
        return triple

    def update(self, answer): 
        self.answer = answer
        self.updateScore(question=self.history[-1],answer=answer)

    def bestQuestion(self):
        ''' This makes use of combinedIndex '''
        highest = max(self.combinedIndex.values())
        indices = [i for i, j in enumerate(self.combinedIndex.values()) if j == highest]
        best = list(self.combinedIndex.keys())[random.choice(indices)]
        return helpers.keyToQuestion(best, self.api)

    def updateScore(self, question = None, answer = None):
        '''
            Here scoreIndex, countIndex and combinedIndex are created upon intilization.
            The scoreIndex updated each question by +10000(yes) and -10000(no).
            The countIndex stays the same throughout the run.
            The combined Index is updated each question.
        '''
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
                    self.combinedIndex[res] = (self.scoreWeight*self.scoreIndex[res]) + (self.entropyWeight*self.entropyIndex[res])
                except: pass
            
            #  delete the entry of the asked question (to no ask it anymore)
            self.scoreIndex.pop( str(question[1]['uri'] + '()()' + question[2]['uri']) )
            self.combinedIndex.pop( str(question[1]['uri'] + '()()' + question[2]['uri']) )
            self.entropyIndex.pop( str(question[1]['uri'] + '()()' + question[2]['uri']) )

        else: # means we just started => intialize score
            for res in results:
                try: self.countIndex[res] += 1 # count
                except: self.countIndex[res] = 1 # else initialize
            
            ''' scoreIndex will contain the scores,
                countIndex will store the counts'''
            self.scoreIndex = {key:1 for key in self.countIndex.keys()}
            totalCount = sum(self.countIndex.values())
            self.entropyIndex = {key:-( (value/totalCount) * np.log2( value/totalCount ) + \
                 ( (totalCount-value) / totalCount )  * np.log2(  (totalCount-value) / totalCount ) )\
             for key,value in self.countIndex.items()}
            self.combinedIndex = {key: (self.scoreWeight*value)+(self.entropyWeight*self.entropyIndex[key]) for key,value in self.scoreIndex.items()}
        