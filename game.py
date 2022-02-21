

from engine.state.main import State
from util import helpers, constants
from bots.Random.bot import RandomBot

class Game:
    nQuestions = 20
    def __init__(self, graph, players=[]): # TODO: load players dynamically.
        self.graph = graph
        self.state = State(self.graph)
        # Players: [Questioner, Answerer]
        self.questioner = RandomBot(self.state)
        self.answerer = 'user'

    def run(self):
        while self.nQuestions > 0:
            question = self.questioner.nextQuestion()
            # answer = input('Is it {}'.format(question))
            def askUser():
                answer = input(question + '? (yes or no) ')
                if answer in constants.POSSIBLE_ANSWERS:
                    self.questioner.update(answer)
                    # self.state.updateGraph(self.questioner.history[-1], answer)
                    self.nQuestions -= 1
                else:
                    input('Please either of {}'.format(constants.POSSIBLE_ANSWERS))
                    askUser()
            askUser()







