from engine.state.main import State
from util import helpers, constants
from bots.Base.bot import BaseBot
from bots.Answerer.bot import Answerer
from bots.Observer.bot import ObserverBot


class Game:
    """
        TODO: Document

    """
    """
    Runs a the game's while loop. The game terminates when the number of asked questions exceeds the QUESTIONS_LIMIT variable in constants.py
    """
    def __init__(self, state=None, nQuestions=constants.QUESTIONS_LIMIT, questioner=None, observer=None, againstHuman = True, devMode = False, observerFlags = {}, corruptedKG = {}, observerStrategy = 'random', currentTournament = None, currentGame = None, observerAdvice = None): # TODO: load players dynamically.
        self.nQuestions = nQuestions
        self.state = state
        # Players: [Questioner, Answerer]
        self.observerFlags = observerFlags
        self.corruptedKG = corruptedKG
        if questioner:
            bot = helpers.load_bot(questioner)
            if questioner in ['CorruptedEntropy', 'CorruptedBase']:
                self.questioner = bot(self.state, self.corruptedKG)
            else:
                self.questioner = bot(self.state)
            #print(type(questioner))
        else:
            self.questioner = BaseBot(self.state)
        self.againstHuman = againstHuman
        self.observerAdvice = observerAdvice
        self.answerer = 'User' if self.againstHuman else Answerer(self.observerAdvice)
        self.devMode = devMode
        self.currentTournament = currentTournament
        self.currentGame = currentGame
        self.observerStrategy = observerStrategy
        self.observer = helpers.load_bot("Observer")(self.state, self.corruptedKG, self.answerer, self.questioner, self.observerFlags, self.observerStrategy, self.currentTournament, self.currentGame)


    # game loop
    def run(self):
        """
        TODO: Document

        """
        while self.state.questionsAsked < self.nQuestions:
            question = self.questioner.nextQuestion()
            if self.againstHuman:
                _,p,_ = question
                while (p['value'] == 'sameAs') or (p['value'] == 'image'):
                    question = self.questioner.nextQuestion()
                    _,p,_ = question
            if self.state.foundAnswer:
                s, p, o = helpers.parseTriple(self.state.foundAnswer)
                if p == 'label':
                    print("It is "+ o)
                elif p == 'image':
                    print("It is "+ helpers.retrieveName(p, self.state.foundAnswer, self.state))
                elif p == 'sameAs':
                    print("It is "+ helpers.retrieveName(p, self.state.foundAnswer, self.state))
                elif p == 'givenName':
                    print("It is "+ helpers.retrieveName(p, self.state.foundAnswer, self.state))
                print(f'Within {self.state.questionsAsked}')
                print("No need for observer as game was won")
                return 1 # 1 indicates the bot has won. 
            
            if not question:
                if self.againstHuman:
                    print( ' No more info ... ')
                    if self.state.yesHints:
                        s, _, _ = self.state.yesHints[-1]
                        answer = input(f'I think it is {helpers.createLabel(s)}, is it correct?')
                        if answer in constants.POSSIBLE_ANSWERS:
                            if answer == 'yes':
                                return 1
                            else: 
                                print('I lost!\n')
                                print('******* START OF OBSERVER *******\n')
                                self.observerFlags, self.observerAdvice = self.observer.observerDecider()
                                return 0
                    else:
                        print('I lost!\n')
                        print('******* START OF OBSERVER *******\n')
                        self.observerFlags, self.observerAdvice = self.observer.observerDecider()
                        return 0
                else:
                    print('I lost, no more info!\n')
                    print('******* START OF OBSERVER *******\n')
                    self.observerFlags, self.observerAdvice = self.observer.observerDecider()
                    return 0

            def askAnswerer(question):
                if self.againstHuman:
                    triple = helpers.parseTriple(question)
                    (_, p, o) = triple
                    readableQuestion =  p + ' ' + o
                    answer = input(readableQuestion + '? (yes or no) ')
                else:
                    answer = self.answerer.getAnswer(question)
                    if self.devMode == True:
                        print('Question: ', " ".join(helpers.parseTriple(question)[1:]), '==> ', answer)

                if answer in constants.POSSIBLE_ANSWERS:
                    self.state.update(question, answer)
                    self.questioner.update(answer)
                    
                else: # Answerer bot will always return a possible answer.
                    print('Please either of {}'.format(constants.POSSIBLE_ANSWERS))
                    askAnswerer(question)
                # print("Look into chosen entity", self.answerer.entity, '\n')
            askAnswerer(question)
        print('Questions limit reached, we lost! \nQuestions Asked:' + str(self.state.questionsAsked))
        print('******* START OF OBSERVER *******\n')
        self.observerFlags, self.observerAdvice = self.observer.observerDecider()
        return 0 # 0 indicates the bot has lost. 
        





