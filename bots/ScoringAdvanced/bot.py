from util import helpers
import numpy as np
from collections import Counter
import random

class ScoringAdvancedBot:
    _name = 'ScoringAdvanced Bot'

    def __init__(self, state):
        self.api = state.api
        self.state = state
        self.scoreIndex = {}
        self.countIndex = {}
        self.combinedIndex = {}
        self.history = []
        self.scoreWeight = 0.9
        self.countWeight = 0.1
        self.inforce = 39730
        self.punish = 2240
        self.updateScore()
        
    def nextQuestion(self):
        triple = self.bestQuestion()
        self.history.append(triple)
        return triple

    def update(self, answer): 
        self.updateScore(question=self.history[-1],answer=answer)

    def bestQuestion(self):
        ''' This makes use of combinedIndex '''
        highest = max(self.combinedIndex.values())
        indices = [i for i, j in enumerate(self.combinedIndex.values()) if j == highest]
        best = list(self.combinedIndex.keys())[random.choice(indices)]
        # best = list(self.combinedIndex.keys())[list(self.combinedIndex.values()).index(highest)]

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
                    self.scoreIndex[res] += self.inforce if answer == 'yes' else -self.punish
                    self.combinedIndex[res] = (self.scoreWeight*self.scoreIndex[res]) + (self.countWeight*self.countIndex[res])
                except: pass
            # print(self.combinedIndex['http://www.w3.org/2000/01/rdf-schema#label()()Taylor Swift'])
            # print(self.scoreIndex['http://www.w3.org/2000/01/rdf-schema#label()()Taylor Swift'])
            # print(self.countIndex['http://www.w3.org/2000/01/rdf-schema#label()()Taylor Swift'],'\n')
            # print(list(self.combinedIndex.keys())[list(self.combinedIndex.values()).index(max(self.combinedIndex.values()))], max(self.combinedIndex.values()))
            # print(list(self.scoreIndex.keys())[list(self.scoreIndex.values()).index(max(self.scoreIndex.values()))], max(self.scoreIndex.values()))
            # print(list(self.countIndex.keys())[list(self.countIndex.values()).index(max(self.countIndex.values()))], max(self.countIndex.values()))
            
            #  delete the entry of the asked question (to no ask it anymore)
            self.scoreIndex.pop( str(question[1]['uri'] + '()()' + question[2]['uri']) )
            self.countIndex.pop( str(question[1]['uri'] + '()()' + question[2]['uri']) )
            self.combinedIndex.pop( str(question[1]['uri'] + '()()' + question[2]['uri']) )

        else: # means we just started => intialize score
            for res in results:
                try: self.countIndex[res] += 1 # count
                except: self.countIndex[res] = 1 # else initialize
            
            ''' scoreIndex will contain the scores,
                countIndex will store the counts'''
            self.scoreIndex = {key:1 for key in self.countIndex.keys()}
            self.combinedIndex = {key: (self.scoreWeight*value)+(self.countWeight*self.countIndex[key]) for key,value in self.scoreIndex.items()}
        
        # print(list(self.scoreIndex.keys())[list(self.scoreIndex.values()).index(max(self.scoreIndex.values()))], \
        #     'which occurs for ', list(self.scoreIndex.values()).count(max(self.scoreIndex.values())))

