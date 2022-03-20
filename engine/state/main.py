from statistics import variance
from util import helpers, api
"""
TODO: Document

"""
class State:
    def __init__(self, depth=0):
        self.api = api.API()
        results = self.api.queryKG()
        # results = helpers.rescursive_query('?p', '?o', self.api)
        # print('first results ', results)
        self.graph = self.api.parseJSON(results)
        self.subGraphs = []
        self.currentDepth = depth
        self.yesHints = []
        self.noHints = []
        self.tripleHistory = []
        self.questionsAsked = 0
        self.foundAnswer = ''
        self._prefixes = {}

      # update the state of the game.
    def update(self, question):
        self.questionsAsked += 1
        prefixes = helpers.parsePrefixes(question)
        for prefix in prefixes:
            self._prefixes[prefix] = True

    # Updates graph each time an answer is given

    def updateGraph(self, question, answer):
        # algorithm for updating the 
        # ...
        #
        # print("You said {}".format(answer))
        answer = answer.lower()
        if answer == 'yes':
            # update graph. Save the p,o into a list
            _, p, _ = helpers.parseTriple(question)
            if p == 'label': # found it! 
                self.foundAnswer = question
                return
        
            self.tripleHistory.append(question)
            self.yesHints.append(question)
        elif answer == 'no':
            self.noHints.append(question)

        self.createSubGraph()

    def createSubGraph(self):
        """
        Minimize the graph each time an answer is given. This function makes use of yesHints and noHints to query the graph.
        """
        prefixes = self.api.prefixes # [f'PREFIX {x}: <{prefix}>' for (prefix, x) in self.api.prefixes.items()]
        
        query = """
        %s
            select *
            where {
                 ?s %s;
                    ?p ?o.
                """%('\n'.join(prefixes),
                    ';'.join([" {} {}".format(p['prefix_entity'], o['prefix_entity']) for (_, p, o) in self.yesHints])) + \
                    helpers.addFilterSPARQL(self.yesHints, self.noHints) + \
                """
            }
        """

        if not self.yesHints: # If no (yes) answers have been given yet.
             query=""" %s
            select * where { ?s a ?o .
                                BIND(<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> AS ?p) """%('\n'.join(prefixes))+ \
                                helpers.addFilterSPARQL(noHints = self.noHints) +"}"
        
        # print(query)
        results = self.api.queryKG(query)
        subGraph = self.api.parseJSON(results, [['s', 'p', 'o']])
        self.subGraphs.append(subGraph)
        self.graph = subGraph

        # for spo in subGraph:
        #     s,p,o = helpers.parseTriple(spo)
        #     if p == 'sameAs':
        #         print('same as is here!!!')
