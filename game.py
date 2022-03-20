

from engine.state.main import State
from util import helpers, constants
from bots.Base.bot import BaseBot
from bots.Answerer.bot import Answerer


class Game:
    """
    Runs a the game's while loop. The game terminates when the number of asked questions exceeds the QUESTIONS_LIMIT variable in constants.py
    """
    def __init__(self, state=State(), nQuestions=constants.QUESTIONS_LIMIT, questioner=None, againstHuman = True): # TODO: load players dynamically.
        self.nQuestions = nQuestions
        self.state = state
        # Players: [Questioner, Answerer]
        self.questioner = questioner or BaseBot(self.state)
        self.againstHuman = againstHuman
        self.answerer = 'User' if self.againstHuman else Answerer()

    # game loop
    def run(self):
        while self.state.questionsAsked < self.nQuestions:
            question = self.questioner.nextQuestion()
            if self.state.foundAnswer:
                s, _, o = helpers.parseTriple(self.state.foundAnswer)
                print("It is "+ o)
                return 1 # 1 indicates the bot has won. 
            if not question:
                if self.againstHuman:
                    print('get last hint: ', self.state.yesHints)#[0]['value'])
                    askAnswerer(self.state.yesHints[-1])
                    break

                    # input(constants.EMPTY_KG)
                else:
                    return 1
                break # TODO: don't break but change the logic based on user's input!
            # answer = input('Is it {}'.format(question))

            def askAnswerer(question):
                if self.againstHuman:
                    # print(question)
                    triple = helpers.parseTriple(question)
                    (_, p, o) = triple
                    readableQuestion =  p + ' ' + o
                    answer = input(readableQuestion + '? (yes or no) ')
                else:
                    answer = self.answerer.getAnswer(question)

                if answer in constants.POSSIBLE_ANSWERS:
                    self.questioner.update(answer)
                    self.state.update(question)
                else: # Answerer bot will always return a possible answer.
                    print('Please either of {}'.format(constants.POSSIBLE_ANSWERS))
                    askAnswerer(question)
            askAnswerer(question)
        return 0 # 0 indicates the bot has lost. 
        





