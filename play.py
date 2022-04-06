
from engine.state.main import State
from game import Game
# from util import helpers
from util import constants
from argparse import ArgumentParser

"""
Running this file in the command line will start the game. 
Some additional arguments are provided for easier execution through the command line.
Arguments:
-d => for development mode TODO WHAT IS THIS??
-n => for number of games TODO WHY SHOULD WE DO THIS??
-f => to choose which dataset to use 
"""
"""
    TODO: Document

"""

## Parse the command line options
parser = ArgumentParser()

parser.add_argument("-q", "--questioner",
                    dest="questioner",
                    help="Choose bot to play with. (default: Base.)",
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

parser.add_argument("-r", "--repository-url",
                    dest="url",
                    help="URL of the repository to be used. (default: True.)",
                    default="http://127.0.0.1:7200/repositories/top2021")

options = parser.parse_args()


numGame = options.games

dev = options.dev

questioner = options.questioner

againstHuman = options.opponent == True

constants.URL = options.url

print('Initializing the game..')
for i in range(numGame):

    print('Running the game..')
    if questioner == 'Entropy' or 'Scoring':
        game = Game(state=State(initializeState=False), questioner=questioner, againstHuman=againstHuman)
    else:
        game = Game(state=State(), questioner=questioner, againstHuman=againstHuman) # TODO: pass players through the CL (Isn't this already done)
    winner = game.run()
    print("The winner ", winner)