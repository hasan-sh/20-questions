import pickle
from util import helpers
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate

class Evaluation:
    def __init__(self) -> None:
        self.result = {}
        self.allResult = {} 

    def evaluate(self):
        for key, data in self.result.items():
            for entity, stats in data.items():
                # [TP, FP],[FN, TN] = stats
                evaluations = self.showResults(stats, entity)
                self.result[key][entity]['evaluation'] = evaluations

    def showResults(self, stats, entity):
        TP = stats['TP']
        FP = stats['FP']
        FN = stats['FN']
        TN = stats['TN']
        print(f"Confusion Matrix: {entity}")
        print("\t   T   F")
        print(f"\tT [{TP}] [{FN}]")
        print(f"\tF [{FP}] [{TN}]")
        precision = TP / (TP + FP + 0.0001)
        recall = TP / (TP + FN + 0.0001)
        accuracy = (TP + TN) / (TP + FP + TN + FN + 0.0001)
        fScore = 2 * ((precision * recall) / (precision + recall + 0.0001))
        evaluations = {
            'p': round(precision, 3),
            'r': round(recall, 3),
            'fs': round(fScore, 3),
            'a': round(accuracy, 3),
        }
        print(entity, evaluations)
        return evaluations
        # heatmap = plt.pcolor(data)
        # plt.title(key) 
        # plt.colorbar(heatmap)
        # plt.show()

    def run(self):
        allResult = {}
        for j in [10, 20, 30, 40]:
            for i in [60, 70, 80, 90]:
        # for j in [30]:
        #     for i in [80]:
                levelsKey = f'{j}_{i}'
                TP = {'Q26876': 0}
                allResult[levelsKey] = {
                                'TP': 0,
                                'FP': 0,
                                'FN': 0,
                                'TN': 0,
                }
                runs = helpers.readPickleBack(f'./new_evaluation_{j}_{i}.pkl')
                # print('\n\n', len(runs))
                runs = runs[0]#[f'{j}_{i}']
                for key, run in runs.items():
                    print('FOR THE ', key)
                    
                    # print(run)
                    for id, item in run.items():
                        # print(item)
                        print('ENTITY: ', id)
                        print('\tall: ', len(item.get('all')))
                        print('\t\tcorrect: ', len(item.get('correct')))
                        allItems = len(item.get('all'))
                        correctItems = len(item.get('correct'))
                        # break
                        # print(allItems, correctItems, item)
                        entity = id
                        if item.get('all'):
                            entity = item.get('all')[0].get('entity')
                        else:
                            print(levelsKey, 'no all !!')

                        if key == 'modelPos':
                            if TP.get(key):
                                TP[key] += all  
                            allResult[levelsKey]['TP'] += correctItems
                            allResult[levelsKey]['FP'] += allItems - correctItems
                            if not allResult[levelsKey].get('correct'):
                                allResult[levelsKey]['correct'] = []
                            allResult[levelsKey]['correct'] += item.get('correct')
                        elif key == 'modelNeg':
                            allResult[levelsKey]['FN'] += correctItems 
                            allResult[levelsKey]['TN'] += allItems - correctItems
                            if not allResult[levelsKey].get('fn'):
                                allResult[levelsKey]['fn'] = []
                            allResult[levelsKey]['fn'] += item.get('correct')
        # self.evaluate()
        # print(allResult)
        result = sorted(allResult.items(), key=lambda x: (-x[1]['TP'], x[1]['FP']))
        statsTable = [[f'File {k}'] + [l for l in v.values() if type(l) == int] for k, v in result]
        labels = ['TP', 'FP', 'FN', 'TN']
        format = 'grid'
        print(tabulate(statsTable, headers=labels, tablefmt=format))
        bestOfAll = 0
        precs = []
        recall = []
        for k, v in result:
            evals = self.showResults(v, k)
            precs.append((k, evals['p']))
            recall.append((k, evals['r']))
            if evals['p'] < 0.9 and evals['p'] > bestOfAll:
                bestPrecision = (k, v, evals)
                bestOfAll = evals['p']
            for i in v.get('correct'):
                print(i[0], i[2])
                print(helpers.parseTriple(i[1].get('triple'), key='uri'), '\n')
            for i in v.get('fn'):
                print(f'\n\n fn NOW: {len(v.get("fn"))} \n\n')
                print(i[0], i[2])
                print(helpers.parseTriple(i[1].get('triple'), key='uri'), '\n')
        
        # print('Best Of All: ', bestPrecision)
        print(precs)
        print(recall)

        # self.saveResults(self.result, 'evaluationEntities.pkl')
        # self.saveResults(self.allResult, 'evaluationSimResults.pkl')
  
    def saveResults(self, results, name):
        with open(name, 'ab') as file: 
            pickle.dump(results, file, pickle.HIGHEST_PROTOCOL)
            print('done')

    def readEvaluations(self):
        bestPrecision = 0
        best = {}
        content = helpers.readPickleBack('evaluationEntities.pkl')
        table = []
        labels = ['TP', 'FP', 'FN', 'TN']
        format = 'grid'
        # format = 'latex'
        bestAndObjTable = {}
        for evaluation in content:
            for key, item in evaluation.items():
                for entity, l in item.items():
                    res = self.showResults(l, f'{key}_{entity}')
                    table.append([f'{key}_{entity}'] + list(res.values()))
                    if not bestAndObjTable.get(f'{key}'):
                        print(key)
                        bestAndObjTable[f'{key}'] = []
                    bestAndObjTable[f'{key}'] += list(res.values())
                    if res['p'] > bestPrecision:
                        bestPrecision = res['p']
                        best = (key, item, res)
                # print(tabulate(table, headers=res.keys(), tablefmt='fancy_grid', floatfmt=".2f"))
                # print(item)
                statsTable = [[f'entity {key}_{e}'] + [l for l in v.values() if type(l) == int] for e, v in item.items()]
                print(tabulate(statsTable, headers=labels, tablefmt=format, floatfmt=".2f"))
                # table=[]
        print(bestAndObjTable)
        print(tabulate(bestAndObjTable, headers='keys', tablefmt=format, floatfmt=".2f"))
        # print(tabulate(table, headers=res.keys(), tablefmt=format, floatfmt=".2f"))
        print('Best of all: ', best)
        bestPrecision = 0

# TEST

e = Evaluation()
# e.readEvaluations()
# e.run()