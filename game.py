

from engine.state.main import State
import util.helpers as helpers
from bots.Random.bot import RandomBot

class Game:
    nQuestions = 20
    def __init__(self, graph, players=[]): # TODO: load players dynamically.
        self.graph = graph
        self.state = State(self.graph)
        self.questioner = RandomBot(self.state)
        self.answerer = 'user'

    def run(self):
        while self.nQuestions > 0:
            question = self.questioner.nextQuestion()
            # answer = input('Is it {}'.format(question))
            answer = input(question + '? (yes or no) ')
            self.questioner.update(answer)
            # self.state.updateGraph(self.questioner.history[-1], answer)
            self.nQuestions -= 1







