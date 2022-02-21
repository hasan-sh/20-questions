
from engine import state
from game import Game
from util import helpers
from argparse import ArgumentParser
import time


def initializeGame(fileName='wikitop2021_small.nt'):
    g = helpers.readGraph(fileName, mode='nt')
    # g = helpers.parseGraph(g)
    return g




## Parse the command line options
parser = ArgumentParser()


parser.add_argument("-p", "--players",
                    dest="players",
                    help="Choose bot to play with. (default: Dummy.)", # TODO: tournament?? so, against bots?!
                    default=['Dummy'])

parser.add_argument("-d", "--development",
                    dest="dev",
                    help="Development mode (default: True.)",
                    default=True)

parser.add_argument("-n", "--number-games",
                    dest="games",
                    help="Number of games to run (default: 1)",
                    default=1)

parser.add_argument("-f", "--dataset-name",
                    dest="fileName",
                    help="Dataset to be used. (default: True.)",
                    default="wikitop2021.nt")

options = parser.parse_args()


numGame = options.games

dev = options.dev

players = options.players

fileName = options.fileName

print('Initializing the game..')
t = time.process_time()
graph = initializeGame(fileName)
elapsed_t = time.process_time() - t
if dev:
    print('It took {}'.format(elapsed_t))
for i in range(numGame):

    print('Running the game..')
    game = Game(graph, players=players) # TODO: pass players through the CL
    game.run()
