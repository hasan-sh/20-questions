"""
Created on Tue Feb 16 16:38:55 2022

@author: hasan-sh
"""
import rdflib
from util import helpers, constants
"""
TODO: Document

"""
class State:
    def __init__(self, graph, depth=0):
        self.graph = graph
        self.subGraphs = []
        self.currentDepth = depth
        self.hints = []
        self.tripleHistory = []
        self.questionsAsked = 0
        self.foundAnswer = ''

    # update the state of the game.
    def update(self):
        self.questionsAsked += 1

    # idea is to update the graph after the user responds
    def updateGraph(self, question, answer):
        # algorithm for updating the do some magic
        # ...
        # ...
        #
        print("You said {}".format(answer))
        answer = answer.lower()
        if answer == 'yes':
            # update graph. Save the prop/obj into a list
            # triples = self.graph.triples(question)
            _, p, _ = helpers.parseTriple(question)
            if p == 'label':
                # found it! 
                self.foundAnswer = question
                return
                
            self.tripleHistory.append(question)
            self.hints.append(question)
            self.createSubGraph(question)
        _, p, o = question
        self.graph.remove((None, p, o))
        # if len(self.graph[:]) < 1: TODO
        #     # reassign graph to the previous one in memory
        #     prevGraph = self.subGraphs[-1]
        #     subjects = prevGraph.subjects()
        #     newGraph = rdflib.Graph()
        #     # p o?
        #     # o = s, p = is it
        #     # is it s?


        # self.graph.remove((None, p, None))


    def createSubGraph(self, question):
        """
        Example: Is it of type Human? If so, we retrieve everyhing that's related to _all human subjects_.
        ?s a Human .
            {
            ?s1 ?p ?s
            }
            union
            {
            ?s ?p1 ?o1
            }
        """
        s, p, o = question
        # TODO: Do we need the union? Fix it!
        query = """
        SELECT *
        WHERE {
            ?s <%s> <%s> .
            {
                ?s1 ?p1 ?s .
            }
            UNION
            {
                ?s ?p2 ?o2 .
            }
        }
        """%(p, o)

        # print(question, query)
        qres = self.graph.query(query)
        subGraph = rdflib.Graph()
        for t in qres:
            if t.s1:
                s1, p1, o1 = t.s1, t.p1, t.s
                subGraph.add((s1, p1, o1))
            if t.p2:
                _, p2, o2 = t.s, t.p2, t.o2
                subGraph.add((s, p2, o2))
            # print(f"{t.s} {t.p} {t.o}")
        self.subGraphs.append(subGraph)
        self.graph = subGraph
