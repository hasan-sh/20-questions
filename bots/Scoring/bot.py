import heapq
from util import helpers
import matplotlib.pyplot as plt
import numpy as np
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
        # print('updating with quesion', self.history[-1], 'and answer', answer)
        self.updateScore(question=self.history[-1],answer=answer)
        # self.state.updateGraph(self.history[-1], answer)

    def bestQuestion(self):
        # totalCount = sum(self.forwardIndex.values())
        # entropy = min(self.forwardIndex.values(), key=lambda x: abs(int(x - int(totalCount) * 0.5)))
        
        # best = list(self.forwardIndex.keys())[list(self.forwardIndex.values()).index(entropy)]
        
        # this takes the highest score
        highest = max(self.forwardIndex.values())
        indices = [i for i, j in enumerate(self.forwardIndex.values()) if j == highest]
        if len(indices) > 1: 
            best = list(self.forwardIndex.keys())[random.choice(indices)]
        else:
            best = list(self.forwardIndex.keys())[indices[0]]

        question = helpers.keyToQuestion(best, self.api)
        # question = [{'value':'','type':'','uri':'','prefix':'','prefix_entity':''}, self.api.memory[str(p)], self.api.memory[str(o)]]
        
        # n = 1
        # while question in self.history:
        #     n += 1
        #     best = list(self.forwardIndex.keys())[list(self.forwardIndex.values()).index(min(heapq.nlargest(n, self.forwardIndex.values())))]
        #     question = helpers.keyToQuestion(best)
        
        # print(question[1]['value'],question[2]['value'])
        
        return question

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

        if answer == 'yes':
            for res in qres:
                try: self.forwardIndex[ str(res[0]['uri'] + '()()' + res[1]['uri']) ] *= 100
                except: pass
            # delete the entry for the yes questions
            self.forwardIndex.pop( str(question[1]['uri'] + '()()' + question[2]['uri']) )
            
        elif answer == 'no':
            for res in qres:
                try: self.forwardIndex[ str(res[0]['uri'] + '()()' + res[1]['uri']) ] *= 0.01
                except: pass        
            #  delete the entry (NOT all triples related) for the no question
            self.forwardIndex.pop( str(question[1]['uri'] + '()()' + question[2]['uri']) )
           
        else: # means we just started => intialize score
            for res in qres:
                try: self.forwardIndex[ str(res[0]['uri'] + '()()' + res[1]['uri']) ] += 1 # count
                except: self.forwardIndex[ str(res[0]['uri'] + '()()' + res[1]['uri']) ] = 1 # else initialize
            # normalize the values in our index
            factor = 1.0/sum(self.forwardIndex.values())
            self.forwardIndex = {key:value*factor for key,value in self.forwardIndex.items()}
        
        # if self.state.questionsAsked > 20:
            # plt.hist(self.forwardIndex.values(),   bins=0.001)
            # plt.show()
        # print(self.forwardIndex['labelTaylor Swift'])
        # print(list(self.forwardIndex.keys())[list(self.forwardIndex.values()).index(max(self.forwardIndex.values()))], \
        #     'which occurs for ', list(self.forwardIndex.values()).count(max(self.forwardIndex.values())))
