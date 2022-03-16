"""
- bot vs answerer
- bot vs human: needed?
"""

import numpy as np
from argparse import ArgumentParser

from engine.state.main import State
from game import Game
from util import helpers


def main(botName, repeat=10, questionLimit=50):
    questionsAsked = np.array([])
    winners = np.array([])
    for i in range(repeat):
        print(f'Playing game #{i+1}')
        state = State()
        bot = helpers.load_bot(botName)
        questioner = bot(state)
        game = Game(state=state, nQuestions=questionLimit, questioner=questioner, againstHuman=False)
        winner = game.run()
        winners = np.append(winners, [winner])
        questionsAsked = np.append(questionsAsked, [state.questionsAsked])
    wonByBot = winners[np.where(winners == 1)].size
    bestGame = np.min(questionsAsked)
    print(f"\n \
    The {botName} bot has won {wonByBot} games. \n \
    Average number of asked questions {round(np.mean(questionsAsked))} out of {questionLimit}.\n \
    Std: {np.std(questionsAsked)}. \n \
    Number of asked questions in the best game {round(bestGame)} out of {questionLimit} \n ")
    


parser = ArgumentParser()

parser.add_argument("-r", "--repeat",
                    dest="repeat",
                    help="Number of games to play (default: 10)", # TODO: tournament?? so, against bots?!
                    type=int,
                    default=10)

parser.add_argument("-p", "--player",
                    dest="player",
                    help="The bot to play against the answerer (default: Base)", # TODO: tournament?? so, against bots?!
                    default='Base')

options = parser.parse_args()
repeat = options.repeat
player = options.player
main(player, repeat)