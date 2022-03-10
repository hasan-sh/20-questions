
from engine import state
from game import Game
from util import helpers
from argparse import ArgumentParser
import time

"""
Running this file in the command line will start the game. 
Some additional arguments are provided for easier execution through the command line.
Arguments:
-p => for players TODO
-d => for development mode TODO
-n => for number of games TODO
-f => to choose which dataset to use 
"""

def initializeGame(fileName='wikitop2021_small.nt'):
    g = helpers.readGraph(fileName, mode='nt')
    # g = helpers.parseGraph(g)
    return g

## Parse the command line options
parser = ArgumentParser()

parser.add_argument("-p", "--questioner",
                    dest="questioner",
                    help="Choose bot to play with. (default: Random.)", # TODO: tournament?? so, against bots?!
                    default=None)

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

questioner = options.questioner

fileName = options.fileName

print('Initializing the game..')
# t = time.process_time()
# # graph = initializeGame(fileName)
# elapsed_t = time.process_time() - t
# if dev:
#     print('It took {}'.format(elapsed_t))
for i in range(numGame):

    print('Running the game..')
    game = Game(questioner=questioner) # TODO: pass players through the CL
    game.run()
