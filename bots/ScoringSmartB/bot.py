from util import helpers
import numpy as np
from collections import Counter
import random

class ScoringSmartBBot:
    _name = 'ScoringSmartB Bot'

    def __init__(self, state):
        self.api = state.api
        self.state = state
        self.countIndex = {}
        self.SSI = {} # SmartScoreIndex
        self.history = []
        self.inforceRelated = 250
        self.punishOthers = 0.5
        self.punishRelated = 0.015
        self.inforceOthers = 2
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

        # best = list(self.SSI.keys())[list(self.SSI.values()).index(highest)]

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
            indexCopy = self.SSI.keys()
            for res in results:
                try:
                    self.SSI[res] += self.inforceRelated if answer == 'yes' else -self.punishRelated
                    indexCopy.remove(res)
                except: pass
            for key in indexCopy: # for all other entries that have not yet been updated
                self.SSI[ key ] *= self.punishOthers if answer == 'yes' else self.inforceOthers
            
            # print(self.SSI['http://www.w3.org/2000/01/rdf-schema#label()()Taylor Swift'])
            # print(list(self.SSI.keys())[list(self.SSI.values()).index(max(self.SSI.values()))], max(self.SSI.values()))

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

        
        # print(list(self.SSI.keys())[list(self.SSI.values()).index(max(self.SSI.values()))], \
        #     'which occurs for ', list(self.SSI.values()).count(max(self.SSI.values())))

