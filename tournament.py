import pickle
import numpy as np
from argparse import ArgumentParser
from engine.state.main import State
from game import Game
from util import constants, helpers
import scipy.stats as st

"""
Running this file in the command line will start the game. 
Some additional arguments are provided for easier execution through the command line.
Arguments:
-r => repreat : int
-p => which bot to play (Entropy, Base, Random)
-url => to choose which dataset to use ( should be running on local server) 
"""

class Tournament:
    """
    TODO: Document

    """
    def __init__(self, botName, repeat=10, questionLimit=constants.QUESTIONS_LIMIT):
        self.botName = botName
        self.repeat = repeat
        self.questionLimit = questionLimit
        
        self.stats = {
            'bot': botName,
            'games': {},
            'questionLimit': questionLimit,
            'repeat': repeat,
        }
            
    def run(self):
        """
        TODO: Document

        """
        questionsAsked = np.array([])
        wonGamesAskedQuestions = np.array([])
        winners = np.array([])
        for i in range(self.repeat):
            print(f'\nPlaying game #{i+1}')
            if self.botName in ['Entropy', 'ScoringBasic', 'ScoringAdvanced', 'ScoringEntropy', 'ScoringEntropy2', 'ScoringSmartA', 'ScoringSmartB']:
                state = State(initializeState=False)
            else:
                state = State()
            game = Game(state=state, nQuestions=self.questionLimit, questioner=self.botName, againstHuman=False)
            winner = game.run()
            winners = np.append(winners, [winner])
            questionsAsked = np.append(questionsAsked, [state.questionsAsked])
            if winner == 1:
                wonGamesAskedQuestions = np.append(wonGamesAskedQuestions, [state.questionsAsked])
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
        
        # for game in self.stats['games']:
            # if self.stats['games'][game]['won'] == 1:
                # wonGamesAskedQuestions = np.append(wonGamesAskedQuestions, [self.stats['games'][game]['questionsAsked'] ])
                # wonGamesAskedQuestions += self.stats['games'][game]['questionsAsked'] 
        print(f"\n \
        The {self.botName} bot has won {wonByBot} games. \n \
        Average number of asked questions {np.round(np.mean(questionsAsked))} out of {self.questionLimit}.\n \
        95% confidence interval all games: {np.round(st.t.interval(alpha=0.95,df=len(questionsAsked)-1, loc=np.mean(questionsAsked), scale=st.sem(questionsAsked)))}\n \
        99% confidence interval all games: {np.round(st.t.interval(alpha=0.99,df=len(questionsAsked)-1, loc=np.mean(questionsAsked), scale=st.sem(questionsAsked)))}\n \
        Average number of asked questions in won games {np.round(np.mean(wonGamesAskedQuestions))} out of {self.questionLimit}.\n \
        95% confidence interval won games: {np.round(st.t.interval(alpha=0.95,df=len(wonGamesAskedQuestions)-1, loc=np.mean(wonGamesAskedQuestions), scale=st.sem(wonGamesAskedQuestions)))} \n \
        99% confidence interval won games: {np.round(st.t.interval(alpha=0.99, df=len(wonGamesAskedQuestions)-1,loc=np.mean(wonGamesAskedQuestions), scale=st.sem(wonGamesAskedQuestions)))}\n \
        Std: {np.std(questionsAsked)}. \n \
        Number of asked questions in the best game {round(bestGame)} out of {self.questionLimit} \n \
        The list of the games is {questionsAsked}")      
          
        self.saveStats(toFile=False)
    # st.t.interval(alpha=0.95, df=len(questionsAsked)-1, loc=np.mean(questionsAsked), scale=st.sem(questionsAsked)) 

    def saveStats(self, toFile=False, short=True):
        """
        TODO: Document

        """
        if toFile:
            oldData = helpers.readPickleBack('.\\20-questions\\tournament_output.pkl')
            with open('.\\20-questions\\tournament_output.pkl', 'wb') as file: 
                pickle.dump(oldData, file)
                pickle.dump(self.stats, file)
        else:
            if short:
                return
            else:
                print(self.stats)

parser = ArgumentParser()

parser.add_argument("-r", "--repeat",
                    dest="repeat",
                    help="Number of games to play (default: 10)",
                    type=int,
                    default=10)

parser.add_argument("-p", "--player",
                    dest="player",
                    help="The bot to play against the answerer (default: Base)",
                    default='Base')

parser.add_argument("-url", "--repository-url",
                    dest="url",
                    help="URL of the repository to be used. (default: True.)",
                    default="http://127.0.0.1:7200/repositories/top2021")


options = parser.parse_args()
repeat = options.repeat
player = options.player
constants.URL = options.url

if __name__ == '__main__':
    tournament = Tournament(player, repeat)
    tournament.run()