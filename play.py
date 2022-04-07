
from engine.state.main import State
from game import Game
# from util import helpers
from util import constants
from argparse import ArgumentParser

"""
Running this file in the command line will start the game. 
Some additional arguments are provided for easier execution through the command line.
Arguments:
-q => which bot to play against (Entropy, Base, Random)
-o => human opponent True or False
-d => for development mode: when in development mode questions and answers are printed
-url => to choose which dataset to use ( should be running on local server) 
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
                    help="Development mode (default: False)",
                    default=False)

parser.add_argument("-url", "--repository-url",
                    dest="url",
                    help="URL of the repository to be used. (default: ... .)",
                    default="http://127.0.0.1:7200/repositories/top2021")

options = parser.parse_args()

dev = options.dev == 'True'

questioner = options.questioner

againstHuman = options.opponent == 'True'

constants.URL = options.url

print('Running the game..')
if questioner == 'Entropy':
    game = Game(state=State(initializeState=False), questioner=questioner, againstHuman=againstHuman, devMode=dev)
else:
    game = Game(state=State(), questioner=questioner, againstHuman=againstHuman, devMode=dev)
winner = game.run()
print("The winner ", winner)