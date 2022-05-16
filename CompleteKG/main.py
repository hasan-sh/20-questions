from copyreg import pickle
import pickle
from alive_progress import alive_bar
import spacy
import time
from transformers import pipeline
import opennre
from operator import itemgetter
from util import helpers
from CompleteKG import helpers as localHelpers

# !pip install wikipedia-api spacy transformers sentence_transformers pytest
# !pip3 uninstall torch torchvision torchaudio #--extra-index-url https://download.pytorch.org/whl/cu113
# !python -m spacy download en_core_web_lg
# pip install git+https://github.com/thunlp/OpenNRE

class CompleteKG:
    def __init__(self, fileName, noHints=True, dev=True) -> None:
        self.nre = opennre.get_model('wiki80_cnn_softmax')
        self.nre.cuda()
        self.bert = pipeline("fill-mask")
        self.nlp = spacy.load('en_core_web_lg')
        self.noHints = noHints
        self.fileName = fileName
        self.runs = helpers.readPickleBack(self.fileName)
        self.dev = dev
        self.stats = {}

    def print(self, *text):
        if self.dev:
            print(text)

    def extractRelations(self, sentence, subj, obj, bert=False, reverse=False): 
        relations = []
        for sub_subj in subj:
            if sub_subj in sentence:
                head_s = sentence.index(sub_subj)
                head_e = head_s + len(sub_subj)
                tail_s = sentence.index(obj)
                tail_e = tail_s + len(obj)
                
                if bert:
                    bestResults = self.bert(f"{sentence} {sub_subj} <mask> {obj} ")
                    # i = np.argmax([cosineSim(x['token_str'], falsePO[0]) for x in bestResults[:2]])# if x['score'] > 0.3])
                    # bestResult = bestResults[i]
                    result = [sub_subj, [[x['token_str'], x['score']] for x in bestResults], obj]
                else:
                    result = [sub_subj,
                                [list(self.nre.infer({'text': sentence, 'h': {'pos': (head_s, head_e)}, 't': {'pos': (tail_s, tail_e)}}))],
                                obj]
                    if reverse:
                        result = [sub_subj,
                                [list(self.nre.infer({'text': sentence, 't': {'pos': (head_s, head_e)}, 'h': {'pos': (tail_s, tail_e)}}))],
                                obj]
                self.print(result)
                    
                relations.append(result)
        return relations

    def validateRelations(self, options, falsePO):
        best = [0, options[0]]
        for option in options:
            for relation in option[1]:
                # self.print('validating ', f'{relation[0]} {option[2]} with', " ".join(falsePO))
                sim = localHelpers.cosineSim(f'{relation[0]} {option[2]}', " ".join(falsePO))
                if best[0] < sim:
                    best = [sim, relation]
        return best
    
    def compareClassifiers(self, sent, subj, obj, falsePO, sentSim):
        # Calculate for NRE
        nreRelations = self.extractRelations(sent.text, subj, obj) # get best 5 candidates, should we consider more?
        _, nreBestRelation = self.validateRelations(nreRelations, falsePO)
        self.print(nreBestRelation, nreRelations)
        self.print('Best NRE Relation Obtained: ', nreBestRelation)
        self.print('From NRE Relations', nreRelations, '\n')

        # Calculate for BERT
        bertRelations = self.extractRelations(sent.text, subj, obj, bert=True) # get best 5 candidates, should we consider more?
        __, bertBestRelation = self.validateRelations(bertRelations, falsePO)
        self.print('Best BERT Relation Obtained: ', bertBestRelation)
        self.print('From BERT Relations', bertRelations, '\n')
        self.print('FALSE PO ',  falsePO)


        # Calculate the similarities and choose the best.
        falsePO = ' '.join(falsePO)

        spo1 = localHelpers.cosineSim(f'{subj[-1]} {nreBestRelation[0]} {obj}', f'{subj[-1]} {falsePO}')[0]
        spo2 = localHelpers.cosineSim(f'{subj[-1]} {bertBestRelation[0]} {obj}', f'{subj[-1]} {falsePO}')[0]

        confidence1 = sentSim * spo1 # * p1 * po1 
        confidence2 = sentSim * spo2 # * p2 * po2

        return {
                'sent': sent.text,
                'obj': obj,
                'model':'nre',  
                'modelsRelation': nreBestRelation,
                'confidence': confidence1[0] 
                } if confidence1 > confidence2 \
            else {
                'sent': sent.text,
                'obj': obj,
                'model': 'bert',
                'modelsRelation': bertBestRelation,
                'confidence': confidence2[0] 
                }
        
    def run(self, acceptenceLevel=0.10):
        self.print('Running main...')
        # self.print(cosineSim('Hasan hates mo', 'mo loves hasan'))
        # history = []
        s = time.time()
        for i, run in enumerate(self.runs):
            print(f'Run no. {i}')
            games = run['games'].values()
            # self.stats[i] = {'hints': hints, 'entity': entity}
            self.stats[i] = {} # assuming per run there's only one game!
            for game in games:
                key = 'noHints' if self.noHints else 'yesHints'
                hints = game[key]
                entity = game['entity']['uri'].rsplit('/', 1)[-1]
                self.stats[i]['entity'] = entity
                subj = entity.split('_')
                subj.append(" ".join(subj))
                doc = self.nlp(localHelpers.getWikiPageText(entity).text) # TODO: Consider a more robust setence splitter.
                with alive_bar(len(hints), dual_line=True, title='Processing...') as bar:
                    totlaCands = self.stats[i].get('total') or 0
                    self.stats[i]['notSelected'] = self.stats[i].get('notSelected') or []
                    self.stats[i]['selected'] = self.stats[i].get('selected') or []
                    self.stats[i]['acceptenceLevel'] = acceptenceLevel
                    for relation in hints: 
                        falsePO = localHelpers.parseRelation(relation)
                        bar.title(' '.join(falsePO))
                        self.print('\nGet Candidates For: ', subj, falsePO[1])
                        candidates = localHelpers.getCandidates(doc.sents, subj, falsePO, acceptenceLevel=0.55) # these are the relavent candidates.
                        candidates.sort(key=itemgetter(1), reverse=True) # sort based on the similarity score between the false object and subject with respect to the sentence.
                        totlaCands += len(candidates) 
                        self.print('Candidates', candidates)
                        bestCandidates = []
                        for sentIndex, (sent, _, obj, sentSim) in enumerate(candidates):
                            self.print(f'SENTENCE no. {sentIndex} ', sent, obj)
                            result = self.compareClassifiers(sent, subj, obj, falsePO, sentSim)
                            bestCandidates.append(result)
                        
                        if bestCandidates:
                            bestCandidate = max(bestCandidates, key=lambda x: x['confidence'])
                            relation.pop(0)
                            relation.insert(0, game['entity'])
                            resultToAdd = {'candidate': bestCandidate, 'triple': relation, 'entity': entity}
                            self.print('best candidates ', bestCandidates)
                            self.print('FINAL CAND. ', bestCandidate)
                            if bestCandidate['confidence'] > acceptenceLevel:
                                # consider not having a threshold at all. 
                                # everything with confidence above 1% could be a true positive; 1, 10, 20, 30, 40..
                                # this will show that setting a threshold is both difficult and cumbersome!
                                
                                self.stats[i]['selected'].append(resultToAdd)

                                bar.text(f'Found {len(self.stats[i]["selected"])} valuable triples!')
                            else:
                                # print(i, self.stats)
                                self.stats[i]['notSelected'].append(resultToAdd)
                        bar()
                    print(totlaCands)

                    self.stats[i]['total'] = totlaCands
                # print(self.stats)
            else:
                self.print('empty', run)
        # for t in triplesToAdd:
        #     print('\nADD the following: ', t, '\n')
        curr_time = (time.time() - s) * 1000
        self.print(curr_time)
        self.saveStats(acceptenceLevel)
        # return triplesToAdd
    
    def saveStats(self, a):

        print("Saving stats..")
        with open(f'./possibleTriples_{int(a*100)}_{55}.pkl', 'ab') as file: 
            pickle.dump(self.stats, file, pickle.HIGHEST_PROTOCOL)
        self.print('Done saving stats.')
        

    
    def runExamples(self):
        print('Running an example...')
        # s = 'The Los Angeles Lakers is a good team. They are an American professional basketball team based in Los Angeles.'
        # s = 'The United States of America (U.S.A. or USA), commonly known as the United States (U.S. or US) or simply America, is a country primarily located in North America.'
        # s = 'Swift was around 12 years old, computer repairman and local musician Ronnie Cremer taught her to play guitar.'
        s = "Swift was 2020's highest-paid musician in the U.S., and highest-paid solo musician worldwide."
        # subject = ['Los Angeles Lakers', 'Los Angeles', 'Lakers', 'Dortmund'] # TODO: use PoS on the subject.
        # subject = ['United States', 'States'] # TODO: use PoS on the subject.
        subject = ['Taylor Swift', 'Taylor', 'Swift'] # TODO: use PoS on the subject.
        # bestO = 'American'
        # bestO = 'guitar'
        bestO = 'musician'
        # bestO = 'North America'

        falsePO = ['has occupation', 'Guitarist']

        sentSim = localHelpers.cosineSim(s, " ".join(falsePO))[0]

        print(self.compareClassifiers(self.nlp(s), subject, bestO, falsePO, sentSim))
    

###########Start extracting################



'''
To pick a prediction of sentance we should have:
    [1: (sent with po),2: (token with o), 3: (predicted relation, falsePO), 4: (predicted PO, falsePO)] 

IDEA: to decide whether to add the found, best triple, we could consider constructing a list
        with all similarities created, take the dot product, and then add it based on a threshold!
    
WHY?
      Sometimes we get a very high similarity from nre and low one for bert. However, the sentence suggests that the falsePO is
        actually true for bert, but not for nre! Example:
        - taylor has occupation Guitarist
            - Best NRE Relation Obtained:  ('Swift', ('instrument', 0.8021246790885925), 'guitar')
            - Best BERT Relation Obtained:  ('Swift', (' plays', 0.5662645697593689), 'guitar')
            - ('bert', 0.53417385, ('Swift', (' plays', 0.5662645697593689), 'guitar'))
        - currently, we do select BERT, because we apply the similarities on the p's and po's and get the mean.
        BUTTTTTT:
        - taylor has occupation Pianist:
            - Best NRE Relation Obtained:  ('Swift', ('occupation', 0.7819189429283142), 'musician')
            - Best BERT Relation Obtained:  ('Swift', (' Solo', 0.14684666693210602), 'musician')
            -('nre', 0.7344303, ('Swift', ('occupation', 0.7819189429283142), 'musician'))
        
        One idea is to check the similarity between guitar and guitarist, and musician and Pianist. However, I believe, this will be problematic later
            on; what threshold to use? words might be very similar which yields lots of false positives!
            ; cosineSim('musician', 'pianist'), cosineSim('guitar', 'guitarist'): (array([[0.7970922]], dtype=float32), array([[0.83837724]], dtype=float32))

'''