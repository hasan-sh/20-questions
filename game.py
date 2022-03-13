

from engine.state.main import State
from util import helpers, constants
from bots.Random.bot import RandomBot
from bots.Answerer.bot import Answerer


class Game:
    """
Here the while loop that keeps the game going on is created. 
The terminal state is when the number of questions asked exceeds the number of allowed questions specificed in util.constants
"""
    def __init__(self, nQuestions=constants.QUESTIONS_LIMIT, questioner=None, againstHuman = True): # TODO: load players dynamically.
        self.nQuestions = nQuestions
        self.state = State()
        # Players: [Questioner, Answerer]
        self.questioner = questioner or RandomBot(self.state)
        self.againstHuman = againstHuman
        self.answerer = 'User' if self.againstHuman else Answerer()

    def run(self):
        while self.state.questionsAsked < self.nQuestions:
            question = self.questioner.nextQuestion()
            if self.state.foundAnswer:
                _, _, o = helpers.parseTriple(self.state.foundAnswer)
                print("It is "+ o)
                return 1 # 1 indicates the bot has won. 
            if not question:
                if self.againstHuman:
                    input(constants.EMPTY_KG)
                break # TODO: don't break but change the logic based on user's input!
            # answer = input('Is it {}'.format(question))

            def askAnswerer(question):
                if self.againstHuman:
                    print(question)
                    triple = helpers.parseTriple(question)
                    (_, p, o) = triple
                    question =  p + ' ' + o
                    answer = input(question + '? (yes or no) ')
                else:
                    answer = self.answerer.getAnswer(question)

                if answer in constants.POSSIBLE_ANSWERS:
                    self.questioner.update(answer)
                    self.state.update()
                else: # Answerer bot will always return a possible answer.
                    print('Please either of {}'.format(constants.POSSIBLE_ANSWERS))
                    askAnswerer(question)
            askAnswerer(question)
        return 0 # 0 indicates the bot has lost. 
        





