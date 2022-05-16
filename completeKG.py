
from argparse import ArgumentParser
import numpy as np
import pickle

from regex import F

from CompleteKG import main
from Evaluation import Evaluation 
from CompleteKG.Validation import Validation
from util import helpers

parser = ArgumentParser()

parser.add_argument("-f", "--file-name",
                    dest="fileName",
                    help="File name to read from (Default: tournament_runs.pkl)",
                    type=str,
                    default="tournament_runs.pkl")

parser.add_argument("-m", "--mode",
                    dest="mode",
                    help="Mode in which to run; normal, test or validate (Default: normal.)",
                    choices=['normal', 'evaluate', 'validate', 'test'],
                    type=str,
                    default='normal')

parser.add_argument("-v", "--verbose",
                    dest="verbose",
                    help="Verbose dev (default: False)",
                    default=False)

parser.add_argument("-n", "--no-hints",
                    dest="noHints",
                    help="Not or yes hints (False: yes hints, True: no hints.)",
                    type=bool,
                    default=True)

options = parser.parse_args()
fileName = options.fileName
mode = options.mode
verbose = options.verbose == True
noHints = options.noHints

# "When mode evaluation, read or run to create a file (Default: True.)",
readOnly = True
# readOnly = False

print(f'MODE: {mode}')
if __name__ == '__main__':
    if mode == 'test':
        completeKG = main.CompleteKG(fileName, noHints, dev=verbose)
        completeKG.runExamples()
    elif mode == 'evaluate':
        evaluate = Evaluation()
        if readOnly:
            evaluate.readEvaluations()
        else:
            evaluate.run()
    elif mode == 'validate':
        validation = Validation()
        for candidateAcceptenceLevel in [10, 20, 30, 40]:
            for objSimAcceptenceLevel in [60, 70, 80]:
        # for candidateAcceptenceLevel in [35]:
        #     for objSimAcceptenceLevel in [55]:
                key = f'{candidateAcceptenceLevel}_{objSimAcceptenceLevel}'
                print(f'Reading ./possibleTriples_{key}.pkl')
                content = helpers.readPickleBack(f'./possibleTriples_{key}.pkl')
                if not content:
                    print('nothing to do', content)
                    exit(0)
                print(len(content[0]), type(content[0]))
                # print(content[0])
                toValidateSelected = {}
                toValidateNotSelected = {}
                # toValidateSelected[f'{candidateAcceptenceLevel}_{objSimAcceptenceLevel}'] = {}
                # toValidateNotSelected[f'{candidateAcceptenceLevel}_{objSimAcceptenceLevel}'] = {}
                for item in content[0].values():
                    entity = item.get('entity')
                    id = validation.getWikidataId(entity)
                    if not toValidateSelected.get(id):
                        toValidateSelected[id] = item.get('selected')
                        toValidateNotSelected[id] = item.get('notSelected')

                validated = validation.validate(toValidateSelected, acceptenceLevel=objSimAcceptenceLevel/100)
                result = {}
                result['modelPos'] = validated # correct predictions by our algo

                print('\nNOT SELECTED\n')
                validated = validation.validate(toValidateNotSelected, acceptenceLevel=objSimAcceptenceLevel/100)
                result['modelNeg'] = validated # incorrect predictions by our algo

                print(f'saving {key}')
                with open(f'./new_evaluation_{key}.pkl', 'ab') as file: 
                    pickle.dump(result, file, pickle.HIGHEST_PROTOCOL)
                    print(f'done {key}')

                    # print(item.get('entity'), item.get('total'), len(item.get('notSelected')), len(item.get('selected')))
                # result = {}
                # result[objSimAcceptenceLevel] = {}
                # for games in runs: #run, games in enumerate(runs):
                #     for i, game in enumerate(games.values()):
                #         result[objSimAcceptenceLevel][i] = {}
                #         toValidateSelected = {}
                #         toValidateNotSelected = {}
                #         entity = game.get('entity')
                #         id = validation.getWikidataId(entity)
                #         if not toValidateSelected.get(id):
                #             toValidateSelected[id] = game.get('selected')
                #             toValidateNotSelected[id] = game.get('notSelected')

                #         print('check on ', toValidateSelected)
                #         correctRelations, allRelations = validation.validate(toValidateSelected, entity, acceptenceLevel=objSimAcceptenceLevel/100)
                #         result[objSimAcceptenceLevel][i][entity] = {}
                #         result[objSimAcceptenceLevel][i][entity]['selected'] = {
                #             'correct': correctRelations,
                #             'total': allRelations,
                #             'modelsPredictions': toValidateSelected[id],
                #             'entity': entity,
                #             'acceptenceLevel': objSimAcceptenceLevel
                #         }
                #         # print('SELECTED VALDIATION correct', len(correctRelations))#, correctRelations, )
                #         # print('SELECTED VALDIATION', len(allRelations))#, allRelations, )
                #         # print('SELECTED VALDIATION model', len(toValidateSelected[id]))#, allRelations, )
                #         # print('check non selected ')
                #         print('check on not selected ', toValidateNotSelected)
                #         correctRelations, allRelations = validation.validate(toValidateNotSelected, entity, acceptenceLevel=objSimAcceptenceLevel/100)
                #         result[objSimAcceptenceLevel][i][entity]['notSelected'] = {
                #             'correct': correctRelations,
                #             'total': allRelations,
                #             'modelsPredictions': toValidateNotSelected[id],
                #             'entity': entity,
                #             'acceptenceLevel': objSimAcceptenceLevel
                #         }
                #         # print('NOT SELECTED VALDIATION correct', len(correctRelations))#, correctRelations, )
                #         # print('NOT SELECTED VALDIATION', len(allRelations))#, allRelations, )
                #         # print('NOT SELECTED VALDIATION model', len(toValidateNotSelected[id]))#, allRelations, )


        # print('relations', correctRelations, allRelations)
        # print(f'{len(correctRelations)} are correct from {len(allRelations)}')
        # print(f'{len(correctRelations)} are correct from {len(allRelations)}')
        
    elif mode == 'normal':
        # for i in [0.10, 0.20, 0.30, 0.40]:
        # for i in [0.25]:
        for i in [0.35]:
            print('Complete KG with aceptence level: ', i)
            completeKG = main.CompleteKG(fileName, noHints, dev=verbose)
            triples = completeKG.run(acceptenceLevel=i)
        # gamesStats = completeKG.stats
        # toValidate = {}
        # for triple in triples:
        #     id = getWikidataId(triple.get('entity'))
        #     if toValidate.get(id):
        #         toValidate[id].append(triple)
        #     else:
        #         toValidate[id] = [triple]
        # # print('stats', gamesStats)
        # print('validating..')#, toValidate)
        # correctRelations, allRelations = validate(toValidate)

        # print('relations', correctRelations, allRelations)
        # print(f'{len(correctRelations)} are correct from {len(allRelations)}')
        # print(f'{len(correctRelations)} are correct from {len(allRelations)}')
        
        print('Next step is to validate the chosen triples by checking their existence on wikidata!!')
        print('python completeKG.py -m validate')
    else:
        print('Unknown argument; ', mode)
        exit(1)
