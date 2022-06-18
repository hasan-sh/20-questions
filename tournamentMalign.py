import pickle
import numpy as np
from argparse import ArgumentParser
from engine.state.main import State
from game import Game
from util import constants, helpers
import pandas as pd
"""
Running this file in the command line will start the game. 
Some additional arguments are provided for easier execution through the command line.
Arguments:
-r => repeat : int
-p => which bot to play (Entropy, Base, Random)
-url => to choose which dataset to use ( should be running on local server) 
"""
class TournamentMalign:
    """
    The Class managing tournaments and the information gathered with these tournaments. 
    
    Attributes
    ----------
    botName : str
        The name of the questioner bot used.
    
    repeat : int
        The amount of times a game is played (default=10).
    
    questionLimit : int
        The amount of questions in which the bot has to guess the target entity.

    Methods
    -------
    run()
       Runs the amount of games specified by the repeat variable and reports the results of those games.

    saveStats(toFile, short)
        Saves the stats from the tournament to a file. 
    """

    def __init__(self, botName, malignType, human, observerStrategy, repeat=10, tournamentCount=100, questionLimit=constants.QUESTIONS_LIMIT):
        self.botName = botName
        self.repeat = repeat
        self.tournamentCount = tournamentCount
        self.questionLimit = questionLimit
        self.observerStrategy = observerStrategy
        self.stats = {
            'bot': botName,
            'games': {},
            'questionLimit': questionLimit,
            'repeat': repeat,
        }
        self.malignErrors = pd.DataFrame({"Run":[], "Old Triple":[], "New Triple":[], "Count":[]}) 
        self.observerFlags = pd.DataFrame({"Run":[], "Type":[], "Triple":[], "Count":[], "Comparison":[], "Subjects":[], "Predicates":[], "Objects":[]})
        # CKG
        self.currentTournament = 58
        self.stateMalign = State() 
        # self.malignBot = helpers.load_bot("Malign")(self.stateMalign, self.currentTournament, self.malignErrors, human = human, malignType = malignType)
        # self.corruptedKG = self.malignBot.corruptedKG
        
            
    def run(self):
        """
        Runs the amount of games specified by the repeat variable and reports the results of those games.

        Parameters -> None

        Returns -> None
        """
        while self.currentTournament < self.tournamentCount: 
            print("\n\n##########################################################################")
            print("###################################", self.currentTournament, "####################################")
            print("##########################################################################\n\n")

            questionsAsked = np.array([])
            winners = np.array([])
            malignBot = helpers.load_bot("Malign")(self.stateMalign, self.currentTournament, self.malignErrors, human = human, malignType = malignType)
            corruptedKG = malignBot.corruptedKG
            observerAdvice = None
            exponent = 1

            for currentGame in range(self.repeat):
                print(f'\n\nPlaying game #{currentGame+1}')
                if self.botName == 'Entropy':
                    state = State(initializeState=False)
                # elif self.botName == 'CorruptEntropy': 
                #     state = State() # else statement in observer works fine here
                #     # state = self.stateMalign # else statement in observer works fine here as well
                else:
                    # state = State()
                    self.stateMalign.tripleHistory = [] ## hier gaat iets fout
                    self.stateMalign.listOfAnswers = []
                    self.stateMalign.yesHints = []
                    self.stateMalign.noHints = []
                    self.stateMalign.foundAnswer = ''
                    self.stateMalign.questionsAsked = 0
                    state = self.stateMalign
                # game = Game(state=state, nQuestions=self.questionLimit, questioner=self.botName, againstHuman = False, observerFlags = self.observerFlags, corruptedKG = self.corruptedKG, observerStrategy = self.observerStrategy, currentTournament = self.currentTournament, currentGame = currentGame)
                game = Game(state=state, nQuestions=self.questionLimit, questioner=self.botName, againstHuman = False, observerFlags = self.observerFlags, corruptedKG = corruptedKG, observerStrategy = self.observerStrategy, currentTournament = self.currentTournament, currentGame = currentGame, observerAdvice = observerAdvice, exponent = exponent)

                winner = game.run()
                self.observerFlags = game.observerFlags
                observerAdvice = game.observerAdvice
                if exponent < game.exponent:
                    exponent = game.exponent
                else:
                    exponent = 1

                winners = np.append(winners, [winner])
                questionsAsked = np.append(questionsAsked, [state.questionsAsked])
                
                self.stats['games'][str(currentGame)] = {
                    "won": winner,
                    # "questioner": questioner.getStats(),
                    "questionsAsked": state.questionsAsked,
                    "yesAnswers": len(state.yesHints),
                    "noAnswers":  len(state.noHints),
                    "yesHints": state.yesHints,
                    "noHints": state.noHints,
                }
            # print("\nThis is observerFlag in 'TournamentMalign':\n\n", self.observerFlags)
            # wonByBot = winners[np.where(winners == 1)].size
            # bestGame = np.min(questionsAsked)
            # self.stats['std'] = np.std(questionsAsked)
            # self.stats['nrQuestionsBestGame'] = round(bestGame)
            
            # print(f"\n \
            # The {self.botName} bot has won {wonByBot} games. \n \
            # Average number of asked questions {round(np.mean(questionsAsked))} out of {self.questionLimit}.\n \
            # Std: {np.std(questionsAsked)}. \n \
            # Number of asked questions in the best game {round(bestGame)} out of {self.questionLimit} \n \
            # This was tournament number: {self.currentTournament}")
            # self.saveStats(toFile=False, short = True)
            # print(self.observerFlags)
            self.observerFlags.to_csv("observerFlags_Save.csv", mode = 'a', header = False, index = False)
            self.observerFlags = pd.DataFrame({"Run":[], "Type":[], "Triple":[], "Count":[], "Comparison":[], "Subjects":[], "Predicates":[], "Objects":[]})
            self.currentTournament += 1
        print("\nFinished!")
            

    def saveStats(self, toFile=False, short=False):
        """
        Saves the stats from the tournament to a file. 

        Parameters
        ----------
        toFile : Boolean
            Determines whether the user wants the results of the tournament saved to a file or not (default=False).

        short : Boolean
            Determines whether the stats should be printed or not (default=True).

        Returns -> None 
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
                    default="http://127.0.0.1:7200/repositories/humans")

parser.add_argument("-m", "--malign type",
                    dest="malignType",
                    help="Malign Type. (default: 1.)",
                    type=int,
                    default=1)

parser.add_argument("-human", "--human",
                    dest="human",
                    help="Human. (default: True)",
                    default="True")

parser.add_argument("-o", "--observer",
                    dest="observer",
                    help="observer. (default: Random)",
                    default="random")

parser.add_argument("-t", "--tournamentCount",
                    dest="tournamentCount",
                    help="Number of tournaments to play (default: 100)",
                    type=int,
                    default=100)


options = parser.parse_args()
malignType = options.malignType
repeat = options.repeat
tournamentCount = options.tournamentCount
player = options.player
human = options.human
observerStrategy = options.observer
constants.URL = options.url

if __name__ == '__main__':
    tournament = TournamentMalign(player, malignType, human, observerStrategy, repeat, tournamentCount)
    tournament.run()