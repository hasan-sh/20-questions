

from engine.state.main import State
from util import helpers, constants
from bots.Random.bot import RandomBot

class Game:
    def __init__(self, graph, nQuestions=constants.QUESTIONS_LIMIT, players=[]): # TODO: load players dynamically.
        self.graph = graph
        self.nQuestions = nQuestions
        self.state = State(self.graph)
        # Players: [Questioner, Answerer]
        self.questioner = RandomBot(self.state)
        self.answerer = 'user' # TODO: update this to be dynamic.

    def run(self):
        while self.state.questionsAsked < self.nQuestions:
            question = self.questioner.nextQuestion()
            # answer = input('Is it {}'.format(question))
            def askUser():
                answer = input(question + '? (yes or no) ')
                if answer in constants.POSSIBLE_ANSWERS:
                    self.questioner.update(answer)
                    self.state.update()
                else:
                    print('Please either of {}'.format(constants.POSSIBLE_ANSWERS))
                    askUser()
            askUser()







