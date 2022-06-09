import rdflib
from rdflib import Graph, URIRef
from util import helpers, constants
import numpy as np
import pandas as pd
import random

"""
TODO: Document
"""
class MalignBot:
    """
    TODO documentation
    """
    _name = 'Malign Bot'

    def __init__(self, state, currentTournament, malignErrors, human, malignType):
        self.state = state
        self.api = self.state.api
        self.graphCopy = self.makeGraph()
        self.malignErrors = malignErrors
        self.currentTournament = currentTournament
        # 'human' refers to the specific dataset under observation
        if human == 'True': 
            self.relations = self.collectRelationsH()
        else: 
            self.relations = self.collectRelations()
        if human == 'True':
            self.subjects = self.collectSubjectsH()

        # 'malignType' refers to the specific manipulation done by malign
        if malignType == 1:
            self.corruptedKG = self.malignRandom(self.currentTournament)
        elif malignType == 2: 
            self.corruptedKG = self.malignOverlap(self.currentTournament)
        elif malignType == 3:
            self.corruptedKG = self.malignSwap(self.currentTournament)
        elif malignType == 4: # manipulation of a single predicate for a subject that holds the predicate
            self.corruptedKG = self.manipulateGraphSP(self.currentTournament)
        elif malignType == 5: # manipulation of all predicates for a subject that holds the predicate
            self.corruptedKG = self.manipulateGraph(self.currentTournament)
        elif malignType == 6: # manipulation of 1%-25% of all predicates in KG
            self.corruptedKG = self.manipulateGraphR(self.currentTournament)
        elif malignType == 7:
            self.corruptedKG = self.manipulateGraphOverlap(self.currentTournament)
        elif malignType == 8:
            self.corruptedKG = self.manipulateGraphSwap(self.currentTournament)
        elif malignType == 9:
            self.corruptedKG = self.malignRandom(self.currentTournament)
        elif malignType == 10: 
            self.corruptedKG = self.malignOverlap(self.currentTournament)
        elif malignType == 10:
            self.corruptedKG = self.malignSwap(self.currentTournament)


    def malignRandom(self, currentTournament): # corresponds to malignType1
        """
        Manipulate the KG created in makeGraph()

        Takes random number of predicates 1-5 and corrupts them
        + adds for every false triples the false triple to 10% of the subjects
        """
        pToCorrupt = random.randint(1, 5)
        predicatesToCorrupt = random.sample(self.relations, pToCorrupt)
        count = 0
        eSToCorrupt = len(self.subjects) // 10

        # print(predicatesToCorrupt)
        for falseRelation in predicatesToCorrupt:
            viralObject = URIRef(np.random.choice(self.saveCorruptObject(falseRelation))) # takes random object from collection of predicates
            # print(viralObject)
            falseP = URIRef(falseRelation) # puts the predicate in the right format for comparison with triples in the graph
            print(falseRelation)
            # Manipulates the graph for a full structural mistakes (all corresponding predicates are manipulated or manipulation is added)
            for triple in self.graphCopy:
                if triple[1] == falseP:
                    old = triple[0], triple[1], triple[2]
                    # print("old:", old)
                    self.graphCopy.set((triple[0], triple[1], viralObject))
                    new = triple[0], triple[1], viralObject
                    # print("new:", new, "\n")
                    self.malignErrors = self.malignErrors.append({"Run":currentTournament, "Old Triple":old, "New Triple":new, "Count":count}, ignore_index=True)
                    count += 1

            # eSubjectsToCorrupt = random.sample(self.subjects, eSToCorrupt)
            # for i in eSubjectsToCorrupt:
            #     subject = URIRef(i)
            #     old = None
            #     # print("old:", old)
            #     self.graphCopy.add((subject, falseP, viralObject))
            #     new = subject, falseP, viralObject
            #     # print("new:", new, "\n")
            #     self.malignErrors = self.malignErrors.append({"Run":currentTournament, "Old Triple":old, "New Triple":new, "Count":count}, ignore_index=True)
            #     count += 1
        print("DF:", self.malignErrors)
        # self.malignErrors.to_csv("malignErrors_Save.csv", mode = 'a', header = False, index = False)
        return self.graphCopy


    def malignOverlap(self, currentTournament): # corresponds to malignType2
        """
        Manipulate the KG created in makeGraph()

        Takes random number of predicates 1-5 and looks for entities that have all these values
        + adds false triples (overlapping) to 10% of the subjects
        """

        PToCorrupt = random.randint(1, 5)
        SToCorrupt = random.randint(25, 125)
        eSToCorrupt = len(self.subjects) // 10

        predicatesToCorrupt = random.choices(self.relations, k=PToCorrupt)
        CSubCandidates = self.overlappingSubjects(predicatesToCorrupt)
        subjectsToCorrupt = random.choices(CSubCandidates, k=SToCorrupt)
        count = 0
        corruptPredicates = []
        corruptSubjects = []
        viralObject = URIRef(np.random.choice(self.saveCorruptObject(random.choice(predicatesToCorrupt)))) # takes random object from collection of predicates

        for predicate in predicatesToCorrupt:
            corruptPredicates.append(URIRef(predicate)) # puts the predicate in the right format for comparison with triples in the graph
        for subject in subjectsToCorrupt:
            corruptSubjects.append(URIRef(subject)) # puts the subject in the right format for comparison with triples in the graph
        
        # Manipulates the graph for a full structural mistake (all corresponding predicates are manipulated)
        for triple in self.graphCopy:
            if (triple[0] in corruptSubjects) and (triple[1] in corruptPredicates):
                    old = triple
                    # print("old:", old)
                    self.graphCopy.set((triple[0], triple[1], viralObject))
                    new = triple[0], triple[1], viralObject
                    # print("new:", new, "\n")

                    self.malignErrors = self.malignErrors.append({"Run":currentTournament, "Old Triple":old, "New Triple":new, "Count":count}, ignore_index=True)
                    count +=1

                    chanceOfRemoval = random.randint(1, 100)
                    if chanceOfRemoval <= 25:
                        corruptSubjects.remove(triple[0])
        
        eSubjectsToCorrupt = random.sample(self.subjects, eSToCorrupt)
        for falseP in corruptPredicates:
            for i in ESubjectsToCorrupt:
                subject = URIRef(i)
                old = None
                # print("old:", old)
                self.graphCopy.add((subject, falseP, viralObject))
                new = subject, falseP, viralObject
                # print("new:", new, "\n")
                self.malignErrors = self.malignErrors.append({"Run":currentTournament, "Old Triple":old, "New Triple":new, "Count":count}, ignore_index=True)
                count += 1
        print("DF:", self.malignErrors)
        # self.malignErrors.to_csv("malignErrors_Save.csv", mode = 'a', header = False, index = False)
        return self.graphCopy

    def malignSwap(self, currentTournament): # corresponds to malignType3
        """
        Manipulate the KG created in makeGraph()

        For random number of subjects, when values some p occurs in both, swap the objects. 
        Plus extra swapped object (with respective predicates) are added to a set of random subject (less than the ones who are swapped)
        """
        PToCorrupt = random.randint(1, 5)
        SToCorrupt = random.randint(100, 150)
        eToCorrupt = random.randint(1, SToCorrupt)

        eSubjectsToCorrupt = random.sample(self.subjects, eToCorrupt)
        currentExtra = 0

        count = 0
        run = 0 
        subjectsToCorrupt = []
        while len(subjectsToCorrupt) == 0:
            try:
                predicatesToCorrupt = random.choices(self.relations, k=PToCorrupt) # takes 1-5 random predicates from all triples
                CSubCandidates = self.overlappingSubjects(predicatesToCorrupt) # generates subjects that have those predicates
                subjectsToCorrupt = random.choices(CSubCandidates, k=SToCorrupt) # takes random sample from the above generated subjects
                print(len(subjectsToCorrupt))
            except:
                print("Exception occured\n")

        for i in range(0, len(subjectsToCorrupt)-2+1, 2):
            pair = subjectsToCorrupt[i:i+2]
            for predicate in predicatesToCorrupt:
                old1 = pair[0], predicate, self.generatePairObject(pair[0], predicate)
                old2 = pair[1], predicate, self.generatePairObject(pair[1], predicate)

                new1 = pair[0], predicate, self.generatePairObject(pair[1], predicate)
                new2 = pair[1], predicate, self.generatePairObject(pair[0], predicate)

                self.graphCopy.set((URIRef(new1[0]), URIRef(new1[1]),URIRef(new1[2])))
                self.graphCopy.set((URIRef(new2[0]), URIRef(new2[1]),URIRef(new2[2])))

                self.malignErrors = self.malignErrors.append({"Run":currentTournament, "Old Triple":old1, "New Triple":new1, "Count":count}, ignore_index=True)
                count+=1
                self.malignErrors = self.malignErrors.append({"Run":currentTournament, "Old Triple":old2, "New Triple":new2, "Count":count}, ignore_index=True)
                count+=1

                try: 
                    toss = random.randint(1, 10)
                    if toss <= 5:
                        extra1 = eSubjectsToCorrupt[currentExtra], predicate, self.generatePairObject(pair[0], predicate)
                    else:
                        extra1 = eSubjectsToCorrupt[currentExtra], predicate, self.generatePairObject(pair[1], predicate)
                    currentExtra += 1

                    self.graphCopy.add((URIRef(extra1[0]), URIRef(extra1[1]),URIRef(extra1[2])))

                    self.malignErrors = self.malignErrors.append({"Run":currentTournament, "Old Triple":None, "New Triple":extra1, "Count":count}, ignore_index=True)
                    count+=1
                except:
                    pass

        print("DF:", self.malignErrors)
        # self.malignErrors.to_csv("malignErrors_Save.csv", mode = 'a', header = False, index = False)
        return self.graphCopy


    def manipulateGraphSP(self, currentTournament): # Corresponds to malignType1
        """
        Manipulate the KG created in makeGraph()
        """
        falseRelation = np.random.choice(self.relations) # takes random predicate from collectRelations 
        viralObject = URIRef(np.random.choice(self.saveCorruptObject(falseRelation))) # takes random object from collection of predicates
        falseP = URIRef(falseRelation) # puts the predicate in the right format for comparison with triples in the graph
        count = 0
        freq = {}

        # Fills a dict for multiple occurrences
        for triple in self.graphCopy:
            if triple[1] == falseP:
                if triple[0] not in freq:
                    freq[triple[0]] = 1
                elif triple[0] in freq:
                    freq[triple[0]] += 1

        # Manipulates the graph but makes sure only one structural mistake is applied
        for triple in self.graphCopy:
            if triple[1] == falseP:
                if freq[triple[0]] == 1:
                    old = triple
                    # print("old triple", old)
                    self.graphCopy.set((triple[0], triple[1], viralObject))
                    new = triple[0], triple[1], viralObject
                    # print("new triple", new, "\n")
                    count +=1
                    self.malignErrors = self.malignErrors.append({"Run":currentTournament, "Old Triple":old, "New Triple":new, "Count":count}, ignore_index=True)
                elif freq[triple[0]] > 1:
                    singleOut = []
                    for secondTriple in self.graphCopy:
                        if secondTriple[0] == triple[0] and secondTriple[1] == triple[1]:
                            singleOut.append(secondTriple)
                    randomOfMultiple = random.choice(singleOut)
                    old = triple
                    # print("old triple", old)
                    self.graphCopy.set((randomOfMultiple[0], randomOfMultiple[1], viralObject))
                    new = triple[0], triple[1], viralObject
                    # print("new triple", new, "\n")
                    count +=1
                    self.malignErrors = self.malignErrors.append({"Run":currentTournament, "Old Triple":old, "New Triple":new, "Count":count}, ignore_index=True)
                    freq[triple[0]] = 0
        # print("DF:", self.malignErrors)
        return self.graphCopy
    

    def manipulateGraph(self, currentTournament): # corresponds to malignType2
        """
        Manipulate the KG created in makeGraph()
        """
        falseRelation = np.random.choice(self.relations) # takes random predicate from collectRelations 
        viralObject = URIRef(np.random.choice(self.saveCorruptObject(falseRelation))) # takes random object from collection of predicates
        falseP = URIRef(falseRelation) # puts the predicate in the right format for comparison with triples in the graph
        count = 0
        print(falseRelation)

        # Manipulates the graph for a full structural mistake (all corresponding predicates are manipulated)
        for triple in self.graphCopy:
            if triple[1] == falseP:
                    old = triple
                    # print("old:", old)
                    self.graphCopy.set((triple[0], triple[1], viralObject))
                    new = triple[0], triple[1], viralObject
                    # print("new:", new, "\n")
                    count +=1
                    self.malignErrors = self.malignErrors.append({"Run":currentTournament, "Old Triple":old, "New Triple":new, "Count":count}, ignore_index=True)
        print("DF:", self.malignErrors)
        return self.graphCopy


    def manipulateGraphR(self, currentTournament): # corresponds to malignType3
        """
        Manipulate the KG created in makeGraph()

        This is a specific function that manipulates a randomized number of predicates
        """
        numberToCorrupt = random.randint(1, 5)
        predicatesToCorrupt = random.sample(self.relations, numberToCorrupt)
        count = 0
        # print(predicatesToCorrupt)
        for falseRelation in predicatesToCorrupt:
            viralObject = URIRef(np.random.choice(self.saveCorruptObject(falseRelation))) # takes random object from collection of predicates
            # print(viralObject)
            falseP = URIRef(falseRelation) # puts the predicate in the right format for comparison with triples in the graph

            # Manipulates the graph for a full structural mistakes (all corresponding predicates are manipulated or manipulation is added)
            for triple in self.graphCopy:
                if triple[1] == falseP:
                    old = triple[0], triple[1], triple[2]
                    # print("old:", old)
                    self.graphCopy.remove((triple[0], triple[1], triple[2]))
                    # new = triple[0], triple[1], viralObject
                    # print("new:", new, "\n")
                    # count +=1
                    # self.malignErrors = self.malignErrors.append({"Run":currentTournament, "Old Triple":old, "New Triple":new, "Count":count}, ignore_index=True)
            for triple in self.graphCopy:
                # old = triple
                # print("old:", old)
                self.graphCopy.add((triple[0], falseP, viralObject))
                new = triple[0], falseP, viralObject
                # print("new:", new, "\n")
                count +=1
                self.malignErrors = self.malignErrors.append({"Run":currentTournament, "Old Triple":old, "New Triple":new, "Count":count}, ignore_index=True)

        print("DF:", self.malignErrors)
        return self.graphCopy


    def manipulateGraphSwap(self, currentTournament): # Corresponds to malignType 5
        """
        Manipulate the KG created in makeGraph()

        For random number of subjects, when values some p occurs in both, swap the objects. 
        """
        PToCorrupt = random.randint(1, 5)
        SToCorrupt = random.randint(25, 75)
        count = 0
        run = 0 
        subjectsToCorrupt = []
        while len(subjectsToCorrupt) == 0:
            try:
                predicatesToCorrupt = random.choices(self.relations, k=PToCorrupt) # takes 1-5 random predicates from all triples
                CSubCandidates = self.overlappingSubjects(predicatesToCorrupt) # generates subjects that have those predicates
                subjectsToCorrupt = random.choices(CSubCandidates, k=SToCorrupt) # takes random sample from the above generated subjects
                print(subjectsToCorrupt)
            except:
                print("Exception occured\n")

        for i in range(0, len(subjectsToCorrupt)-2+1, 2):
            pair = subjectsToCorrupt[i:i+2]
            # print("\nPair information:", pair[0], pair[1])
            for predicate in predicatesToCorrupt:
                # print("\n\nPredicate:\n", predicate, "\n")
                old1 = pair[0], predicate, self.generatePairObject(pair[0], predicate)
                old2 = pair[1], predicate, self.generatePairObject(pair[1], predicate)

                new1 = pair[0], predicate, self.generatePairObject(pair[1], predicate)
                new2 = pair[1], predicate, self.generatePairObject(pair[0], predicate)

                self.graphCopy.set((URIRef(new1[0]), URIRef(new1[1]),URIRef(new1[2])))
                self.graphCopy.set((URIRef(new2[0]), URIRef(new2[1]),URIRef(new2[2])))
                # print("This is old 1:\n", old1)
                # print("This is new 1:\n", new1)
                # print("This is old 2:\n", old2)
                # print("This is new 2:\n", new2)

                count+=1
                self.malignErrors = self.malignErrors.append({"Run":currentTournament, "Old Triple":old1, "New Triple":new1, "Count":count}, ignore_index=True)
                count+=1
                self.malignErrors = self.malignErrors.append({"Run":currentTournament, "Old Triple":old2, "New Triple":new2, "Count":count}, ignore_index=True)
        
        print("DF:", self.malignErrors)
        return self.graphCopy

    
    def manipulateGraphOverlap(self, currentTournament): # corresponds to malign type 4
        """
        Manipulate the KG created in makeGraph()

        For some random number of objects when the objects share in 2-5 predicates, only then manipulate the objects
        """
        PToCorrupt = random.randint(1, 5)
        SToCorrupt = random.randint(25, 75)

        predicatesToCorrupt = random.choices(self.relations, k=PToCorrupt)
        CSubCandidates = self.overlappingSubjects(predicatesToCorrupt)
        subjectsToCorrupt = random.choices(CSubCandidates, k=SToCorrupt)
        count = 0
        corruptPredicates = []
        corruptSubjects = []
        viralObject = URIRef(np.random.choice(self.saveCorruptObject(random.choice(predicatesToCorrupt)))) # takes random object from collection of predicates

        for predicate in predicatesToCorrupt:
            corruptPredicates.append(URIRef(predicate)) # puts the predicate in the right format for comparison with triples in the graph
        for subject in subjectsToCorrupt:
            corruptSubjects.append(URIRef(subject)) # puts the subject in the right format for comparison with triples in the graph
        
        # Manipulates the graph for a full structural mistake (all corresponding predicates are manipulated)
        for triple in self.graphCopy:
            if (triple[0] in corruptSubjects) and (triple[1] in corruptPredicates):
                    old = triple
                    # print("old:", old)
                    self.graphCopy.set((triple[0], triple[1], viralObject))
                    new = triple[0], triple[1], viralObject
                    # print("new:", new, "\n")
                    count +=1
                    self.malignErrors = self.malignErrors.append({"Run":currentTournament, "Old Triple":old, "New Triple":new, "Count":count}, ignore_index=True)
                    chanceOfRemoval = random.randint(1, 100)
                    if chanceOfRemoval <= 25:
                        corruptSubjects.remove(triple[0])
        print("DF:", self.malignErrors)
        return self.graphCopy

    
    def overlappingSubjects(self, predicatesToCorrupt):
        if len(predicatesToCorrupt) == 1:
            query = """select ?s where {
                    ?s """ + '<' + predicatesToCorrupt[0] + '>' + """ ?o
                    }"""

        elif len(predicatesToCorrupt) == 2:
            query = """select distinct ?s where { 
                    ?s """ + '<' + predicatesToCorrupt[0] + '>' + """ ?k.
                    ?s """ + '<' + predicatesToCorrupt[1] + '>' + """ ?l.
                    }"""
        
        elif len(predicatesToCorrupt) == 3:
            query = """select distinct ?s where {
                    ?s """ + '<' + predicatesToCorrupt[0] + '>' + """ ?k.
                    ?s """ + '<' + predicatesToCorrupt[1] + '>' + """ ?l.
                    ?s """ + '<' + predicatesToCorrupt[2] + '>' + """ ?m.
	                }"""

        elif len(predicatesToCorrupt) == 4:
            query = """select distinct ?s where { 
                    ?s """ + '<' + predicatesToCorrupt[0] + '>' + """ ?k.
                    ?s """ + '<' + predicatesToCorrupt[1] + '>' + """ ?l.
                    ?s """ + '<' + predicatesToCorrupt[2] + '>' + """ ?m.
                    ?s """ + '<' + predicatesToCorrupt[3] + '>' + """ ?o.
	                }"""

        elif len(predicatesToCorrupt) == 5:
            query = """select distinct ?s where {
                    ?s """ + '<' + predicatesToCorrupt[0] + '>' + """ ?k.
                    ?s """ + '<' + predicatesToCorrupt[1] + '>' + """ ?l.
                    ?s """ + '<' + predicatesToCorrupt[2] + '>' + """ ?m.
                    ?s """ + '<' + predicatesToCorrupt[3] + '>' + """ ?o.
                    ?s """ + '<' + predicatesToCorrupt[4] + '>' + """ ?p.
	                }"""
        qres = self.api.queryKG(query=query)
        qres = self.api.parseJSON(qres, [['s']])
        qres = [x[0]['uri'] for x in qres if len(x) == 1] 
        return qres # qres contains candidate subjects for manipulation


    def saveCorruptObject(self, falseRelation):
        falseP = '<' + falseRelation + '>'
        # print("False Relation: ", falseRelation)
        query = """select ?o where {
            ?s """ + falseP + """ ?o }"""
        qres = self.api.queryKG(query=query)
        qres = self.api.parseJSON(qres, [['o']])
        qres = [x[0]['uri'] for x in qres if len(x) == 1] 
        return qres # qres contains objects that belong to the given predicate


    def generatePairObject(self, swapSubject, swapPredicate):
        swapP = '<' + swapPredicate + '>'
        swapS = '<' + swapSubject + '>'
        query = """select ?o where {
        """ + swapS + swapP + """ ?o }"""
        qres = self.api.queryKG(query=query)
        qres = self.api.parseJSON(qres, [['o']])
        qres = [x[0]['uri'] for x in qres if len(x) == 1]
        randomObject = random.choice(qres) # qres contains objects that belong to the given predicate
        return randomObject


    def collectRelations(self):
        """
        Collects all the predicates that exist within the KG that is created in makeGraph()
        """
        query = """select distinct ?p where {?s ?p ?o}"""
        qres = self.api.queryKG(query=query)
        qres = self.api.parseJSON(qres, [['p']])
        qres = [x[0]['uri'] for x in qres] # check if the [0] is needed
        return qres
    
    def collectSubjectsH(self):
        query = """select distinct ?s 
                where { 
	            ?s rdf:type <http://yago-knowledge.org/resource/Human>} 
                """
        qres = self.api.queryKG(query=query)
        qres = self.api.parseJSON(qres, [['s']])
        qres = [x[0]['uri'] for x in qres]
        return qres


    def collectRelationsH(self):
        """
        Collects all the predicates that exist within the KG that is created in makeGraph() except for some entity specific relations
        """
        query = """ SELECT distinct ?p
        WHERE {
        ?x ?p ?o
        FILTER (
            !EXISTS {
                    {
                        {
                            {?x <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?o}
                            Union
                            {?x <http://www.w3.org/2000/01/rdf-schema#subPropertyOf> ?o}
                        }
                        Union
                        {
                            {?x <http://www.w3.org/2000/01/rdf-schema#domain> ?o}
                            Union
                            {?x <http://www.w3.org/2000/01/rdf-schema#range> ?o}
                        }
                    }
                    Union
                    {
                        {
                            {?x <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?o}
                            Union
                            {?x <http://www.w3.org/2002/07/owl#sameAs> ?o}
                        }
                        Union
                        {
                            {?x <http://proton.semanticweb.org/protonsys#transitiveOver> ?o}
                            Union
                            {?x <http://www.w3.org/2002/07/owl#inverseOf> ?o}
                        }
                    }
                    Union
                    {
                            {?x <http://www.w3.org/2000/01/rdf-schema#label> ?o}
                            Union
                            {?x <http://schema.org/image> ?o}
                    }
                    }
        )
        }"""
        qres = self.api.queryKG(query=query)
        qres = self.api.parseJSON(qres, [['p']])
        qres = [x[0]['uri'] for x in qres]
        return qres
    

    def makeGraph(self):
        """
        Makes a copy from the KG that is used by the endpoint on GraphDB. This graph is later on manipulated.
        """
        query = """select * where {?s ?p ?o}"""
        qres = self.api.queryKG(query=query)
        qres = self.api.parseJSON(qres, [['s', 'p', 'o']])
        qres = [[x[0]['uri'], x[1]['uri'], x[2]['uri']] for x in qres if len(x) == 3] # for each triple
        self.graphCopy = rdflib.Graph()
        for res in qres:
            self.graphCopy.add((URIRef(res[0]), URIRef(res[1]), URIRef(res[2])))
        return self.graphCopy