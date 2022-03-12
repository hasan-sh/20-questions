"""
Created on Tue Feb 16 16:38:55 2022

@author: hasan-sh
"""
from statistics import variance
import rdflib
from util import helpers, constants, api
"""
TODO: Document

"""
class State:
    def __init__(self, depth=0):
        self.api = api.API()
        results = self.api.queryKG()
        self.graph = self.api.parseJSON(results)
        self.subGraphs = []
        self.currentDepth = depth
        self.yesHints = []
        self.noHints = []
        self.tripleHistory = []
        self.questionsAsked = 0
        self.foundAnswer = ''

    # update the state of the game.
    def update(self):
        self.questionsAsked += 1

    # idea is to update the graph after the user responds
    def updateGraph(self, question, answer):
        # algorithm for updating the 
        # ...
        #
        print("You said {}".format(answer))
        answer = answer.lower()
        if answer == 'yes':
            # update graph. Save the prop/obj into a list
            _, p, _ = helpers.parseTriple(question)
            if p == 'label': # found it! 
                self.foundAnswer = question
                return
        
            self.tripleHistory.append(question)
            self.yesHints.append(question)
        elif answer == 'no':
            self.noHints.append(question)

        self.createSubGraph(question)
        # print("@@@@@@@@@@@@@@@@@@@@@@@",self.yesHints, self.noHints)


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
        
        """
            each time
                - look at history:
                    - hints: [(s0p0o0), (s1p1o1), ...]
                    - create a query backward; hints[-1:0] --> ?s p0 o0;
                                                                  p1 o1;
                                                                  p2 o2;
                                                                  p3 o3.
                                                                ?s ?p ?o.
                    - we have the subgraph!
        """
        # yesHints = [" <{}> <{}>".format(p, o) for (_, p, o) in self.yesHints]
        # query = """
        #     select *
        #     where {
        #         ?s %s.
        #         ?s ?p ?o. """%(';'.join(yesHints)) + \
        #          helpers.addFilterSPARQL(self.yesHints, self.noHints) + \
        #         """
        #     }
        # """
        # print(query)
        # results = self.api.queryKG(query)
        # subGraph = self.api.parseJSON(results, [['s', 'p', 'o']])
        # self.subGraphs.append(subGraph)
        # self.graph = subGrap


        # yesHints = [" <{}> <{}>".format(p, o) for (_, p, o) in self.yesHints] # none of those could be labels
        query = """
            select *
            where {
                ?s %s.
                {?s ?p ?o.}
                UNION
                {?s1 ?p1 ?s}"""%(';'.join([" <{}> <{}>".format(p, o) for (_, p, o) in self.yesHints])) + \
                 helpers.addFilterSPARQL(self.yesHints, self.noHints) + \
                """
            }
        """
        if not self.yesHints: # If no (yes) answers have been given yet.
            query="""select * where { ?s a ?o .
                                                BIND('http://www.w3.org/1999/02/22-rdf-syntax-ns#type' AS ?p) """+ \
                                                helpers.addFilterSPARQL(noHints = self.noHints) +"""}"""
        
        print(query)
        results = self.api.queryKG(query)
        # subGraph = self.api.parseJSON(results, [['s', 'p', 'o'],['s1', 'p1', 's']])
        subGraph = self.api.parseJSON(results, [['s', 'p', 'o'],['s', 'p1', 's1']])
        # print(question, query)
        self.subGraphs.append(subGraph)
        self.graph = subGraph
        
