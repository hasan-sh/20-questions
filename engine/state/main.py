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

    # update the state of the game.
    def update(self):
        self.questionsAsked += 1

    # idea is to update the graph after the user responds
    def updateGraph(self, question, answer):
        # algorithm for updating the 
        # ...
        #
        # print("You said {}".format(answer))
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

        self.createSubGraph()

    def createSubGraph(self):
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

        
        query = """
            select *
            where {
                ?s %s.
                {?s ?p ?o.}
                UNION
                {?s1 ?p1 ?s}"""%(';'.join([" <{}> <{}>".format(p['value'], o['value']) for (_, p, o) in self.yesHints])) + \
                 helpers.addFilterSPARQL(self.yesHints, self.noHints) + \
                """
            }
        """
        if not self.yesHints: # If no (yes) answers have been given yet.
            query="""select * where { ?s a ?o .
                                                BIND('http://www.w3.org/1999/02/22-rdf-syntax-ns#type' AS ?p) """+ \
                                                helpers.addFilterSPARQL(noHints = self.noHints) +"""}"""
        
        # print(query)
        results = self.api.queryKG(query)
        subGraph = self.api.parseJSON(results, [['s', 'p', 'o'],['s', 'p1', 's1']])
        self.subGraphs.append(subGraph)
        self.graph = subGraph
        
