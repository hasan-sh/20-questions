
from engine.state.main import State
from game_rsearch import Game
# from util import helpers
from util import constants
from argparse import ArgumentParser
import numpy as np

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

# params = {'weights':[ [0.1,0.9], [0.2,0.8], [0.3,0.7] ],
#           'inc':np.random.choice(np.arange(100,100000,10), 6),
#           'dec':np.random.choice(np.arange(100,100000,10), 6)}

# params = {'weights':[ [0.4,0.6], [0.5,0.5], [0.6,0.4] ],
#           'inc':np.random.choice(np.arange(100,100000,10), 6),
#           'dec':np.random.choice(np.arange(100,100000,10), 6)}

params = {'weights':[ [0.7,0.3], [0.8,0.2] ,[0.9,0.1] ],
          'inc':np.random.choice(np.arange(100,100000,10), 6),
          'dec':np.random.choice(np.arange(100,100000,10), 6)}


# # print('Running the game..')
a = []
best = 400
for w in params['weights']:
    for i in params['inc']:
        for d in params['dec']:
            param = {'weights':w, 'inc':i, 'dec':d}
            game = Game(state=State(initializeState=False), questioner= 'Scoring', againstHuman=againstHuman, devMode=dev, params = param)
            winner = game.run()
            if best > game.state.questionsAsked:
                best = game.state.questionsAsked
                a.append(param)

print(param, best)
