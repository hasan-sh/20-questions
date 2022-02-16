"""
Created on Tue Feb 16 16:38:55 2022

@author: hasan-sh
"""



class State:
    def __init__(self, graph, depth=0):
        self.graph = graph
        self.currentDepth = depth
        self.hints = []

    # idea is to update the graph after the user responds
    def updateGraph(self, question, answer):
        # algorithm for updating the do some magic
        # ...
        # ...
        #
        print( answer)
        if answer == 'yes':
            # update graph. Save the prop/obj into a list
            self.hints.append(question)
        self.graph.remove(question)
