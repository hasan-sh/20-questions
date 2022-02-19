"""
Created on Tue Feb 16 16:38:55 2022

@author: hasan-sh
"""
import rdflib

class State:
    def __init__(self, graph, depth=0):
        self.graph = graph
        self.subGraphs = []
        self.currentDepth = depth
        self.hints = []
        self.tripleHistory = []

    # idea is to update the graph after the user responds
    def updateGraph(self, question, answer):
        # algorithm for updating the do some magic
        # ...
        # ...
        #
        print( answer)
        if answer == 'yes':
            # update graph. Save the prop/obj into a list
            # triples = self.graph.triples(question)
            self.tripleHistory.append(question)
            self.hints.append(question)
            self.createSubGraph(question)
        s, p, o = question
        # print('REMOVE: ', s,p,o)
        self.graph.remove((None, p, o))

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
                    ?s ?p ?o .
        }
        """%(p, o)#.format(p, o)
        # print(query)
                # {
                #     ?s1 ?p ?s
                # }
                # UNION
                # {
                #     ?s ?p1 ?o1
                # }

        qres = self.graph.query(query)
        subGraph = rdflib.Graph()
        for t in qres:
            subGraph.add(t)
            print(f"{t.s} {t.p} {t.o}")
        self.subGraphs.append(subGraph)
