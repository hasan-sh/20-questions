"""
- bot vs answerer
- bot vs human: needed?
"""

import importlib
import numpy as np
from argparse import ArgumentParser

from engine.state.main import State
from game import Game
from util import helpers, constants
from bots.Random.bot import RandomBot
from bots.Answerer.bot import Answerer

def load_bot(name):
    """
    name: The folder name of the bot.
    """
    path = f'bots.{name}.bot'
    # print(f'Importing {path}')
    module = importlib.import_module(path)
    bot = getattr(module, f'{name}Bot')
    return bot
    # bot = botClass()

    # print(bot)

def main(botName, repeat=10, questionLimit=50):
    questionsAsked = np.array([])
    winners = np.array([])
    for i in range(repeat):
        print(f'Playing game #{i+1}')
        state = State()
        # Players: [Questioner, Answerer]
        bot = load_bot(botName)
        questioner = bot(state)
        game = Game(nQuestions=questionLimit, questioner=questioner, againstHuman=False)
        winner = game.run()
        winners = np.append(winners, [winner])
        questionsAsked = np.append(questionsAsked, [state.questionsAsked])
    wonByBot = winners[np.where(winners == 0)].size
    averages = np.array([])
    for q in questionsAsked:
        averages = np.append(averages, [q/questionLimit])
    averageWins = np.mean(averages)
    bestGame = np.min(questionsAsked)
    print(f"The ({botName}) bot has won {wonByBot} games with an average of {averageWins}. \n The best game {bestGame}")
    


parser = ArgumentParser()

parser.add_argument("-r", "--repeat",
                    dest="repeat",
                    help="Number of games to play (default: 10)", # TODO: tournament?? so, against bots?!
                    type=int,
                    default=10)

parser.add_argument("-p", "--player",
                    dest="player",
                    help="The bot to play against the answerer (default: Random)", # TODO: tournament?? so, against bots?!
                    default='Random')

options = parser.parse_args()
repeat = options.repeat
player = options.player
main(player, repeat)