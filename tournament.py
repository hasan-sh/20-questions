"""
- bot vs answerer
- bot vs human: needed?
"""

# from asyncio import constants
import numpy as np
from argparse import ArgumentParser

from engine.state.main import State
from game import Game
from util import helpers, constants

class Tournament:
    def __init__(self, botName, repeat=10, questionLimit=constants.QUESTIONS_LIMIT) -> None:
        self.botName = botName
        self.repeat = repeat
        self.questionLimit = questionLimit
        
        self.stats = {
            'bot': botName,
            'games': {
                # 1: {
                # "won": winner,
                # "nr_questions_asked": questionsAsked,
                # "yes_answers": len(game.state.yesHints),
                # "no_answers":  len(game.state.noHints),
                # "yes_hints": game.state.yesHints,
                # "no_hints": game.state.noHints
                # }
            },
            'questionLimit': questionLimit,
            'repeat': repeat
            # 'std': np.std(questionsAsked)
        }
            
    def run(self):
        questionsAsked = np.array([])
        winners = np.array([])
        for i in range(self.repeat):
            print(f'Playing game #{i+1}')
            state = State()
            game = Game(state=state, nQuestions=self.questionLimit, questioner=self.botName, againstHuman=False)
            winner = game.run()
            winners = np.append(winners, [winner])
            questionsAsked = np.append(questionsAsked, [state.questionsAsked])
            
            self.stats['games'][str(i)] = {
                "won": winner,
                # "questioner": questioner.getStats(),
                "questionsAsked": state.questionsAsked,
                "yesAnswers": len(state.yesHints),
                "noAnswers":  len(state.noHints),
                "yesHints": state.yesHints,
                "noHints": state.noHints,
            }
        wonByBot = winners[np.where(winners == 1)].size
        bestGame = np.min(questionsAsked)
        self.stats['std'] = np.std(questionsAsked)
        self.stats['nrQuestionsBestGame'] = round(bestGame)
        
        print(f"\n \
        The {self.botName} bot has won {wonByBot} games. \n \
        Average number of asked questions {round(np.mean(questionsAsked))} out of {self.questionLimit}.\n \
        Std: {np.std(questionsAsked)}. \n \
        Number of asked questions in the best game {round(bestGame)} out of {self.questionLimit} \n ")
        self.saveStats(toFile=False)

    def saveStats(self, toFile=False, short=True):
        if toFile:
            with open('tournament_output.txt','w') as data: 
                data.write(str(self.stats))
        else:
            if short:
                return
            else:
                print(self.stats)
        


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

if __name__ == '__main__':
    # print('Tournament: ', player)
    tournament = Tournament(player, repeat)
    tournament.run()