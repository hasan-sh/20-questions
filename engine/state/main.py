from util import helpers, api
from bots.Malign.bot import MalignBot
import rdflib
from rdflib import URIRef

class State:

    """
    The Class handling the updating of the game state. 
    
    Attributes
    ----------
    depth : int
        --

    initializeState : Boolean
        Decides whether the state should be initialized, meaning that either the bot will start with the KG queried
        on type or not. 

    Methods
    -------
    update(question, answer)
        Keeps track of the amount of questions asked and what questions are answered yes/no to, each time a question is asked. 

    updateGraph()?

    createSubGraph()
        Minimize the graph each time an answer is given. This function makes use of yesHints and noHints to query the graph.

    """
    def __init__(self, depth=0, initializeState = True):
        self.api = api.API()
        if not initializeState:
            self.graph = []
        else:
            results = self.api.queryKG()
            self.graph = self.api.parseJSON(results)
        self.currentDepth = depth
        self.listOfAnswers = []
        self.yesHints = []
        self.noHints = []
        self.tripleHistory = []
        self.questionsAsked = 0
        self.foundAnswer = ''
        self._prefixes = {}
        self.history = [] # last results
        # self.malignBot = helpers.load_bot("Malign")(self)
        # # print("IN MAIN -print type of corruptedGraph:", type(self.corruptedKG.manipulateGraphSP()))
        # self.corruptedKG = self.malignBot.corruptedKG


      # update the state of the game.
    def update(self, question, answer):
        """
        Keeps track of the amount of questions asked and what questions are answered yes/no to, each time a question is asked. 
        If yes is answered to a question about a label, the question gets added to found answer. 

        Parameters 
        ----------
        question : str
            The triple of the question asked
        
        answer : str
            A yes/no response to the question.

        Returns -> None

        """
        self.questionsAsked += 1
        self.tripleHistory.append(question)
        answer = answer.lower()
        self.listOfAnswers.append(answer)
        if answer == 'yes':
            # update graph. Save the p,o into a list
            _, p, _ = helpers.parseTriple(question)
            if p  in ['label', 'image', 'givenName', 'sameAs']: # found it! 
                self.foundAnswer = question
                return
        
            self.yesHints.append(question)
        elif answer == 'no':
            self.noHints.append(question)

        # print("MAIN - list of answers and triple history: ", self.listOfAnswers, self.tripleHistory)
    # Updates graph each time an answer is given

    def updateGraph(self, question, answer):
        """
        TODO: Document ??

        """
        self.createSubGraph()

    def createSubGraph(self):
        """
        Minimizes the graph each time an answer is given. This function makes use of yesHints and noHints to query the graph.
        If no yesAnswers have been given yet, it will limit the subGraph to types, while filtering out the rejected triples. 

        Parameters -> None

        Returns -> None
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
        
        results = self.api.queryKG(query)
        subGraph = self.api.parseJSON(results, [['s', 'p', 'o']])
        self.graph = subGraph


    def createSubGraphX(self, answer, corruptedKG):

        """
        Minimizes the graph each time an answer is given. This function makes use of yesHints and noHints to query the graph.
        If no yesAnswers have been given yet, it will limit the subGraph to types, while filtering out the rejected triples. 

        Parameters -> None

        Returns -> None
        """
        # prefixes = self.api.prefixes # [f'PREFIX {x}: <{prefix}>' for (prefix, x) in self.api.prefixes.items()]
        
        # query = """select *
        #     where {
        #         ?s %s;
        #             ?p ?o.
        #         """ + ';'.join([" {} {}".format(p['uri'], o['uri']) for (_, p, o) in self.yesHints]) + \
        #             helpers.addFilterSPARQLX(self.yesHints, self.noHints) + \
        #         """
        #     }
        # """

        query = f"""
            SELECT *
            WHERE {{
            ?s ?p ?o ;
                {';'.join([" <{}> <{}>".format(p['uri'], o['uri']) for (_, p, o) in self.yesHints])} .
                {helpers.addFilterSPARQLX(yesHints=self.yesHints, noHints=self.noHints)}    
            }}
            """

        if not self.yesHints: # If no (yes) answers have been given yet.
            query="""select * where { ?s a ?o .
                                BIND(<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> AS ?p) """+ \
                                helpers.addFilterSPARQLX(noHints = self.noHints)+ """}"""
            # query="""select * where { ?s ?p ?o ."""+ \
            #                     helpers.addFilterSPARQLX(noHints = self.noHints)+ """}"""
        
        results = corruptedKG.query(query)
        # if not results:
        #     print('results is empty', query)
        #     if (URIRef("http://yago-knowledge.org/resource/Joe_Biden"), None, None) in corruptedKG:
        #         print("after, blabla in base")
        res = self.api.parseJSONX(results, [['s', 'p', 'o']])
        # if not res: 
        #     print('res is empty')
        # self.graph = subGraph
        qres = [[x[0]['uri'], x[1]['uri'], x[2]['uri']] for x in res if len(x) == 3] # for each triple
        # if not qres:
        #     print('qres is empty')
        subgraph = rdflib.Graph()
        for res in qres:
            subgraph.add((URIRef(res[0]), URIRef(res[1]), URIRef(res[2])))
        # if not subgraph:
        #     print('graph is empty!')
        return subgraph
