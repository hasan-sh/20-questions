
from engine import state
from game import Game
from util import helpers
from argparse import ArgumentParser

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

parser.add_argument("-q", "--questioner",
                    dest="questioner",
                    help="Choose bot to play with. (default: Base.)", # TODO: tournament?? so, against bots?!
                    default=None)

parser.add_argument("-o", "--human-opponent",
                    dest="opponent",
                    help="Playing against a human or a bot (Default: True)",
                    default=True)

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

questioner = helpers.load_bot(options.questioner) if options.questioner else options.questioner

againstHuman = options.opponent == True

fileName = options.fileName

print('Initializing the game..')
for i in range(numGame):

    print('Running the game..')
    game = Game(questioner=questioner, againstHuman=againstHuman) # TODO: pass players through the CL
    winner = game.run()
    print("The winner ", winner)