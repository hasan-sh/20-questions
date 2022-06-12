from util import helpers
import numpy as np
from collections import Counter
import random

class EC2Bot:
    _name = 'EC2 Bot'

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
        
    def nextQuestion(self):
        triple = self.bestQuestion()
        self.history.append(triple)
        return triple

    def update(self, answer): 
        self.answer = answer
        self.updateScore(question=self.history[-1],answer=answer)

    def bestQuestion(self):
        ''' DOWN makes use of only score '''

        highest = max(self.scoreIndex.values())
        indices = [i for i, j in enumerate(self.scoreIndex.values()) if j == highest]
        best = list(self.scoreIndex.keys())[random.choice(indices)]

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

            #  delete the entry of the asked question (to no ask it anymore)
            self.scoreIndex.pop( str(question[1]['uri'] + '()()' + question[2]['uri']) )
            self.countIndex.pop( str(question[1]['uri'] + '()()' + question[2]['uri']) )

        else: # means we just started => intialize score
            for res in results:
                try: self.countIndex[res] += 1 # count
                except: self.countIndex[res] = 1 # else initialize
            ''' scoreIndex will contain the entropy scores,
                countIndex will store the counts'''

            totalCount = sum(self.countIndex.values())
            self.scoreIndex = {key:-( (value/totalCount) * np.log2( value/totalCount ) + \
                 ( (totalCount-value) / totalCount )  * np.log2(  (totalCount-value) / totalCount ) )\
             for key,value in self.countIndex.items()}
            