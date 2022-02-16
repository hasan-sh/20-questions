

from engine.state.main import State
import util.helpers as helpers
from bots.Random.bot import RandomBot

class Game:
    nQuestions = 20
    def __init__(self):
        g = helpers.readGraph('datasets/wikitop2021.nt', mode='nt')
        self.graph = helpers.parseGraph(g)
        self.state = State(self.graph)
        self.questioner = RandomBot(self.state)
        self.answerer = 'user'

    def run(self):
        while self.nQuestions > 0:
            question = self.questioner.nextQuestion(self.state)
            # answer = input('Is it {}'.format(question))
            answer = input(question + '? (yes or no) ')
            self.state.updateGraph(self.questioner.history[-1], answer)
            self.nQuestions -= 1







print('Initializing the game..')
game = Game()
print('Running the game..')
game.run()
