import collections
from util import helpers
import pandas as pd
import random

class ObserverBot:
    """
    TODO documentation
    """
    _name = 'Observer Bot'

    def __init__(self, state, corruptedKG, answerer, questioner, observerFlags, observerStrategy, currentTournament = 0, currentGame = 0):
        self.state = state
        self.answerer = answerer
        self.questioner = questioner
        self.observerFlags = observerFlags
        self.corruptedKG = corruptedKG
        self.observerType = observerStrategy
        self.currentGame = currentGame
        self.currentTournament = currentTournament
        self.api = self.state.api
    

    def observerDecider(self):
        """
        Decides with value which observer is used
        """
        if self.observerType == "greedyP":
            print("Observer = greedyP\n")
            observerFlags, observerAdvice = self.greedyPObserver()
            print("******* END OF OBSERVER *******\n")
            return observerFlags, observerAdvice

        elif self.observerType == "greedyO":
            print("Observer = greedyO\n")
            observerFlags, observerAdvice = self.greedyOObserver()
            print("******* END OF OBSERVER *******\n")
            return observerFlags, observerAdvice
        
        elif self.observerType == "greedyPcool":
            print("Observer = greedyPcool\n")
            observerFlags, observerAdvice = self.greedyPcoolObserver()
            print("******* END OF OBSERVER *******\n")
            return observerFlags, observerAdvice
        
        elif self.observerType == "greedyOcool":
            print("Observer = greedyOcool\n")
            observerFlags, observerAdvice = self.greedyPcoolObserver()
            print("******* END OF OBSERVER *******\n")
            return observerFlags, observerAdvice
        
        elif self.observerType == "greedyPglobal":
            print("Observer = greedyPcool\n")
            observerFlags, observerAdvice = self.greedyPGlobalObserver()
            print("******* END OF OBSERVER *******\n")
            return observerFlags, observerAdvice
        
        elif self.observerType == "greedyOglobal":
            print("Observer = greedyOGlobal\n")
            observerFlags, observerAdvice = self.greedyPGlobalObserver()
            print("******* END OF OBSERVER *******\n")
            return observerFlags, observerAdvice

        elif self.observerType == "random":
            print("Observer = randomObserver\n")
            return self.randomObserver()


    def randomObserver(self):
        """
        Take triples from expert (human or flawless answerer)
        """
        questionsAsked = self.state.tripleHistory
        listOfAnswers = self.state.listOfAnswers
        chosenEntity = self.answerer.entity
        falseKGEntity = self.corruptedKG 
        # print("\nTrue entity according to expert = ", chosenEntity[0]["uri"])

        # for question in questionsAsked:
        #     print(question[1]["uri"], question[2]["uri"])
        # print(listOfAnswers)

        count = 1 # needs to be connected to state
        for question, answer in zip(questionsAsked, listOfAnswers):
            flagSwitch = False
            if answer == 'no': # flag: 'no' is given by expert but attribute/triple of the question is included in the corrupted KG
                for attribute in falseKGEntity: #Go through all relations in the KG
                    attribute0 = str(attribute[0])
                    attribute1 = str(attribute[1])
                    attribute2 = str(attribute[2])

                    if chosenEntity[0]["uri"] == attribute0 and question[1]["uri"] == attribute1 and question[2]["uri"] == attribute2: # if relation occurs -> flag it                    
                        combinedAttributes = attribute0 + " " + attribute1 + " " + attribute2
                        if self.observerFlags.empty: # condition -> cannot check empty df
                            print("1a Flag it")
                            self.observerFlags = self.observerFlags.append({"Run":self.currentTournament, "Type": 1, "Triple":attribute, "Count":count, "Comparison":combinedAttributes, "Subjects":attribute0, "Predicates":attribute1, "Objects":attribute2}, ignore_index=True)
                            count +=1
                        elif (combinedAttributes in self.observerFlags['Comparison'].unique()) is False:
                            print("1b Flag it")
                            self.observerFlags = self.observerFlags.append({"Run":self.currentTournament, "Type": 1, "Triple":attribute, "Count":count, "Comparison":combinedAttributes, "Subjects":attribute0, "Predicates":attribute1, "Objects":attribute2}, ignore_index=True)
                            count +=1
                        flagSwitch = True

            elif answer == "yes": # flag: 'yes' is given by expert but attribute/triple of the question is not included in the corrupted KG
            # This might not be possible, since the answerer cannot question something that it doesn't
                switch = False
                for attribute in falseKGEntity:
                    attribute0 = str(attribute[0])
                    attribute1 = str(attribute[1])
                    attribute2 = str(attribute[2])
                    if chosenEntity[0]["uri"] == attribute0 and question[1]["uri"] == attribute1 and question[2]["uri"] == attribute2:
                        switch = True
                        break
                if switch == False:
                    print("2 Flag it")
                    combinedAttributes = attribute0 + " " + attribute1 + " " + attribute2
                    if  self.observerFlags.empty:
                            self.observerFlags = self.observerFlags.append({"Run":self.currentTournament, "Type": 2, "Triple":attribute, "Count":count, "Comparison":combinedAttributes, "Subjects":attribute0, "Predicates":attribute1, "Objects":attribute2}, ignore_index=True)
                            count +=1
                    elif self.observerFlags["Comparison"].str.contains(combinedAttributes).count() == 0:
                        self.observerFlags = self.observerFlags.append({"Run":self.currentTournament, "Type": 2, "Triple":attribute, "Count":count, "Comparison":combinedAttributes, "Subjects":attribute0, "Predicates":attribute1, "Objects":attribute2}, ignore_index=True)
                        count += 1
                    flagSwitch = True
            if flagSwitch == True:
                break
        # print("\nobserverFlags in the randomObserver function:")
        print(self.observerFlags)
        return self.observerFlags

    
    def greedyPObserver(self):
        """
        Observer mode that follows the greedy predicate observer strategy.
        A df with flags of wrong entities is considered and the most recurring wrong predicate is picked
        """

        rows = len(self.observerFlags.axes[0])

        if rows < 2: # dit gaat om de rows in the dataframe
            print("If statement in greedyP\n")
            self.observerFlags = self.randomObserver()
            return self.observerFlags, None
        else: 
            print("Else statement in greedyP\n")
            self.observerFlags = self.randomObserver()

            FrequentPredicate = self.observerFlags['Predicates'].value_counts().index.tolist()[:5][0]
            FrequencyPredicate = self.observerFlags['Predicates'].value_counts().values.tolist()[:5][0]

            newEntity = self.pickNewEntity(FrequentPredicate, FrequencyPredicate, 'predicate')
            print("This is the new Triple", newEntity, type(newEntity))
            return self.observerFlags, newEntity


    def greedyOObserver(self):

        rows = len(self.observerFlags.axes[0])
        print("print rows", rows)
        
        if rows < 2: # dit gaat om de rows in the dataframe
            print("If statement in greedyO\n")
            self.observerFlags = self.randomObserver()
            return self.observerFlags, None
        else: 
            print("Else statement In greedyO\n")
            self.observerFlags = self.randomObserver()
    
            FrequentObject = self.observerFlags['Objects'].value_counts().index.tolist()[:5][0]
            FrequencyObject = self.observerFlags['Objects'].value_counts().values.tolist()[:5][0]

            newEntity = self.pickNewEntity(FrequentObject, FrequencyObject, 'object')
            print("This is the new Triple", newEntity, type(newEntity))
            return self.observerFlags, newEntity
    
    def greedyPcoolObserver(self):
        """
        Observer mode that follows the greedy predicate observer strategy.
        A df with flags of wrong entities is considered and the most recurring wrong predicate is picked
        """

        rows = len(self.observerFlags.axes[0])
        if rows < 2: # dit gaat om de rows in the dataframe
            print("If statement in greedyP\n")
            self.observerFlags = self.randomObserver()
            return self.observerFlags, None
        else: 
            print("Else statement in greedyP\n")
            self.observerFlags = self.randomObserver()

            FrequentPredicateList = self.observerFlags['Predicates'].value_counts().index.tolist()[:5][0]
            FrequencyPredicateList = self.observerFlags['Predicates'].value_counts().values.tolist()[:5][0]

            randomizer = random.randint(1, 31)
            if randomizer == 1 and len(FrequenctPredicateList) == 5:
                FrequentPredicate = FrequenctPredicateList[4]
                FrequencyPredicate = FrequencyPredicateList[4]
            elif randomizer <= 3 and len(FrequenctPredicateList) == 4:
                FrequenctPredicate = FrequenctPredicateList[3]
                FrequencyPredicate = FrequencyPredicateList[3]
            elif randomizer <= 7 and len(FrequenctPredicateList) == 3:
                FrequenctPredicate = FrequenctPredicateList[2]
                FrequencyPredicate = FrequencyPredicateList[2]
            elif randomizer <= 15 and len(FrequenctPredicateList) == 2:
                FrequenctPredicate = FrequenctPredicateList[1]
                FrequencyPredicate = FrequencyPredicateList[1]
            else:
                FrequenctPredicate = FrequenctPredicateList[0]
                FrequencyPredicate = FrequencyPredicateList[0]

            newEntity = self.pickNewEntity(FrequentPredicate, FrequencyPredicate, 'predicate')
            print("This is the new Triple", newEntity, type(newEntity))
            return self.observerFlags, newEntity

    def greedyOcoolObserver(self):
        """
        Observer mode that follows the greedy predicate observer strategy.
        A df with flags of wrong entities is considered and the most recurring wrong predicate is picked
        """

        rows = len(self.observerFlags.axes[0])

        if rows < 2: # dit gaat om de rows in the dataframe
            print("If statement in greedyP\n")
            self.observerFlags = self.randomObserver()
            return self.observerFlags, None
        else: 
            print("Else statement in greedyP\n")
            self.observerFlags = self.randomObserver()

            FrequentObjectList = self.observerFlags['Predicates'].value_counts().index.tolist()[:5]
            FrequencyObjectList = self.observerFlags['Predicates'].value_counts().values.tolist()[:5]

            randomizer = random.randint(1, 31)
            if randomizer == 1 and len(FrequentObjectList) == 5:
                FrequentObject = FrequentObjectList[4]
                FrequencyObject = FrequencyObjectList[4]
            elif randomizer <= 3 and len(FrequentObjectList) == 4:
                FrequentObject = FrequentObjectList[3]
                FrequencyObject = FrequencyObjectList[3]
            elif randomizer <= 7 and len(FrequentObjectList) == 3:
                FrequentObject = FrequentObjectList[2]
                FrequencyObject = FrequencyObjectList[2]
            elif randomizer <= 15 and len(FrequentObjectList) == 2:
                FrequentObject = FrequentObjectList[1]
                FrequencyObject = FrequencyObjectList[1]
            else:
                FrequentObject = FrequentObjectList[0]
                FrequencyObject = FrequencyObjectList[0]

            newEntity = self.pickNewEntity(FrequentPredicate, FrequencyPredicate, 'predicate')
            print("This is the new Triple", newEntity, type(newEntity))
            return self.observerFlags, newEntity


    def greedyPGlobalObserver(self):
        """
        Observer mode that follows the greedy predicate observer strategy.
        A df with flags of wrong entities is considered and the most recurring wrong predicate is picked
        """

        rows = len(self.observerFlags.axes[0])


        if rows < 2: # dit gaat om de rows in the dataframe
            print("If statement in greedyP\n")
            self.observerFlags, newFound = self.randGlobalAssist()
            print(newFound, type(newFound))
            exit()
            guessPossible(newFound)
            
            return self.observerFlags, None
        else: 
            print("Else statement in greedyP\n")
            self.observerFlags, newFound = self.randGlobalAssist()

            newPredicate = str(newFound[1])
            # if self.observerFlags['Predicate'].str.contains(newPredicate).any()

            FrequentPredicateList = self.observerFlags['Predicates'].value_counts().index.tolist()[:][0]
            FrequencyPredicateList = self.observerFlags['Predicates'].value_counts().values.tolist()[:][0]

            randomizer = random.randint(1, 31)
            if randomizer == 1 and len(FrequenctPredicateList) == 5:
                FrequentPredicate = FrequenctPredicateList[4]
                FrequencyPredicate = FrequencyPredicateList[4]
            elif randomizer <= 3 and len(FrequenctPredicateList) == 4:
                FrequenctPredicate = FrequenctPredicateList[3]
                FrequencyPredicate = FrequencyPredicateList[3]
            elif randomizer <= 7 and len(FrequenctPredicateList) == 3:
                FrequenctPredicate = FrequenctPredicateList[2]
                FrequencyPredicate = FrequencyPredicateList[2]
            elif randomizer <= 15 and len(FrequenctPredicateList) == 2:
                FrequenctPredicate = FrequenctPredicateList[1]
                FrequencyPredicate = FrequencyPredicateList[1]
            else:
                FrequenctPredicate = FrequenctPredicateList[0]
                FrequencyPredicate = FrequencyPredicateList[0]

            newEntity = self.pickNewEntity(FrequentPredicate, FrequencyPredicate, 'predicate')
            print("This is the new Triple", newEntity, type(newEntity))
            return self.observerFlags, newEntity

    def greedyOGlobalObserver(self):
        """
        Observer mode that follows the greedy predicate observer strategy.
        A df with flags of wrong entities is considered and the most recurring wrong predicate is picked
        """

        rows = len(self.observerFlags.axes[0])

        if rows < 2: # dit gaat om de rows in the dataframe
            print("If statement in greedyP\n")
            self.observerFlags = self.randomObserver()
            return self.observerFlags, None
        else: 
            print("Else statement in greedyP\n")
            self.observerFlags = self.randomObserver()

            FrequentObjectList = self.observerFlags['Predicates'].value_counts().index.tolist()[:5]
            FrequencyObjectList = self.observerFlags['Predicates'].value_counts().values.tolist()[:5]

            randomizer = random.randint(1, 31)
            if randomizer == 1 and len(FrequentObjectList) == 5:
                FrequentObject = FrequentObjectList[4]
                FrequencyObject = FrequencyObjectList[4]
            elif randomizer <= 3 and len(FrequentObjectList) == 4:
                FrequentObject = FrequentObjectList[3]
                FrequencyObject = FrequencyObjectList[3]
            elif randomizer <= 7 and len(FrequentObjectList) == 3:
                FrequentObject = FrequentObjectList[2]
                FrequencyObject = FrequencyObjectList[2]
            elif randomizer <= 15 and len(FrequentObjectList) == 2:
                FrequentObject = FrequentObjectList[1]
                FrequencyObject = FrequencyObjectList[1]
            else:
                FrequentObject = FrequentObjectList[0]
                FrequencyObject = FrequencyObjectList[0]

            newEntity = self.pickNewEntity(FrequentPredicate, FrequencyPredicate, 'predicate')
            print("This is the new Triple", newEntity, type(newEntity))
            return self.observerFlags, newEntity
    
    def pickNewEntity(self, frequent, frequency, tripleEntity):
        if tripleEntity == 'object':
                query = """select distinct ?s where {
                        ?s ?p """ + '<' + frequent + '>' + """.
                        # ?s <rdfs:label> ?o.
                        }"""
        elif tripleEntity == 'predicate':
                query = """select distinct ?s where {
                        ?s """ + '<' + frequent + '>' + """ ?o.
                        # ?s <rdfs:label> ?o.
                        }"""
        qres = self.api.queryKG(query=query)
        qres = self.api.parseJSON(qres, [['s']])
        qres = [x[0]['uri'] for x in qres]
        newTriple = random.choice(qres)
        return newTriple # new candidate for expert


    def guessPossible(self, newFound):
        # newFound =
        querry = """select distinct ?s where { 
	        ?s <""" + + """> ?o .
            }"""


    def randGlobalAssist(self):
        """
        Take triples from expert (human or flawless answerer)
        """
        questionsAsked = self.state.tripleHistory
        listOfAnswers = self.state.listOfAnswers
        chosenEntity = self.answerer.entity
        falseKGEntity = self.corruptedKG 
        # print("\nTrue entity according to expert = ", chosenEntity[0]["uri"])

        for question in questionsAsked:
            print(question[1]["uri"], question[2]["uri"])
        print(listOfAnswers)

        count = 1 # needs to be connected to state
        for question, answer in zip(questionsAsked, listOfAnswers):
            flagSwitch = False
            if answer == 'no': # flag: 'no' is given by expert but attribute/triple of the question is included in the corrupted KG
                for attribute in falseKGEntity: #Go through all relations in the KG
                    attribute0 = str(attribute[0])
                    attribute1 = str(attribute[1])
                    attribute2 = str(attribute[2])

                    if chosenEntity[0]["uri"] == attribute0 and question[1]["uri"] == attribute1 and question[2]["uri"] == attribute2: # if relation occurs -> flag it                    
                        combinedAttributes = attribute0 + " " + attribute1 + " " + attribute2
                        if self.observerFlags.empty: # condition -> cannot check empty df
                            print("1a Flag it")
                            self.observerFlags = self.observerFlags.append({"Run":self.currentTournament, "Type": 1, "Triple":attribute, "Count":count, "Comparison":combinedAttributes, "Subjects":attribute0, "Predicates":attribute1, "Objects":attribute2}, ignore_index=True)
                            count +=1
                            newFound = attribute
                        elif (combinedAttributes in self.observerFlags['Comparison'].unique()) is False:
                            print("1b Flag it")
                            self.observerFlags = self.observerFlags.append({"Run":self.currentTournament, "Type": 1, "Triple":attribute, "Count":count, "Comparison":combinedAttributes, "Subjects":attribute0, "Predicates":attribute1, "Objects":attribute2}, ignore_index=True)
                            count +=1
                            newFound = attribute
                        flagSwitch = True

            elif answer == "yes": # flag: 'yes' is given by expert but attribute/triple of the question is not included in the corrupted KG
            # This might not be possible, since the answerer cannot question something that it doesn't
                switch = False
                for attribute in falseKGEntity:
                    attribute0 = str(attribute[0])
                    attribute1 = str(attribute[1])
                    attribute2 = str(attribute[2])
                    if chosenEntity[0]["uri"] == attribute0 and question[1]["uri"] == attribute1 and question[2]["uri"] == attribute2:
                        switch = True
                        break
                if switch == False:
                    print("2 Flag it")
                    combinedAttributes = attribute0 + " " + attribute1 + " " + attribute2
                    if  self.observerFlags.empty:
                            self.observerFlags = self.observerFlags.append({"Run":self.currentTournament, "Type": 2, "Triple":attribute, "Count":count, "Comparison":combinedAttributes, "Subjects":attribute0, "Predicates":attribute1, "Objects":attribute2}, ignore_index=True)
                            count +=1
                            newFound = attribute
                    elif self.observerFlags["Comparison"].str.contains(combinedAttributes).count() == 0:
                        self.observerFlags = self.observerFlags.append({"Run":self.currentTournament, "Type": 2, "Triple":attribute, "Count":count, "Comparison":combinedAttributes, "Subjects":attribute0, "Predicates":attribute1, "Objects":attribute2}, ignore_index=True)
                        count += 1
                        newFound = attribute
                    flagSwitch = True
            if flagSwitch == True:
                break
        # print("\nobserverFlags in the randomObserver function:")
        # print(self.observerFlags)
        return self.observerFlags, newFound

