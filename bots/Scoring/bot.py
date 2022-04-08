from util import helpers
import numpy as np
from collections import Counter
import random

class ScoringBot:
    _name = 'Scoring Bot'

    def __init__(self, state):
        self.api = state.api
        self.state = state
        self.forwardIndex = {}
        self.updateScore()
        self.history = []
        
    def nextQuestion(self):
        triple = self.bestQuestion()
        self.history.append(triple)
        return triple

    def update(self, answer): 
        self.updateScore(question=self.history[-1],answer=answer)

    def bestQuestion(self):
        # totalCount = sum(self.forwardIndex.values())
        # entropy = min(self.forwardIndex.values(), key=lambda x: abs(int(x - int(totalCount) * 0.5)))
        # best = list(self.forwardIndex.keys())[list(self.forwardIndex.values()).index(entropy)]
        
        # sums = dict(Counter(self.forwardIndex) + Counter(self.countIndex))
        # means = {k: sums[k] / 2 for k in sums}
        # highest = max(means.values())
        # best = list(means.keys())[list(means.values()).index(highest)]

        highest = max(self.forwardIndex.values())
        indices = [i for i, j in enumerate(self.forwardIndex.values()) if j == highest]
        if len(indices) > 1: 
            best = list(self.forwardIndex.keys())[random.choice(indices)]
        else:
            best = list(self.forwardIndex.keys())[indices[0]]

        # best = list(self.forwardIndex.keys())[list(self.forwardIndex.values()).index(highest)]

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
            indexCopy = self.forwardIndex.keys()
            for res in results:
                try:
                    self.forwardIndex[res] *= 250 if answer == 'yes' else 0.01
                    indexCopy.remove(res)
                except: pass
            for key in indexCopy:
                self.forwardIndex[ key ] *= 0.5 if answer == 'yes' else 2
            #  delete the entry of the asked question (to no ask it anymore)
            self.forwardIndex.pop( str(question[1]['uri'] + '()()' + question[2]['uri']) )
           
        else: # means we just started => intialize score
            for res in results:
                try: self.forwardIndex[res] += 1 # count
                except: self.forwardIndex[res] = 1 # else initialize
            ## normalize the values in our index
            # factor = 1.0/sum(self.forwardIndex.values())
            # self.forwardIndex = {key:value*factor for key,value in self.forwardIndex.items()}

        # print(self.forwardIndex['http://www.w3.org/2000/01/rdf-schema#label()()Taylor Swift'])
        # print(list(self.forwardIndex.keys())[list(self.forwardIndex.values()).index(max(self.forwardIndex.values()))], \
        #     'which occurs for ', list(self.forwardIndex.values()).count(max(self.forwardIndex.values())))

