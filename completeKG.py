from statistics import mode
from util import helpers
import wikipediaapi
import spacy
import re
import time
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import opennre
from sklearn.metrics.pairwise import cosine_similarity
from argparse import ArgumentParser
import numpy as np
from operator import itemgetter
from util import helpers

# !pip install wikipedia-api spacy transformers sentence_transformers pytest
# !pip3 uninstall torch torchvision torchaudio #--extra-index-url https://download.pytorch.org/whl/cu113
# !python -m spacy download en_core_web_lg
# pip install git+https://github.com/thunlp/OpenNRE

model_embedding = SentenceTransformer('all-mpnet-base-v2')
model_embedding.cuda()
model_re = opennre.get_model('wiki80_cnn_softmax')
model_re.cuda()
model_BERT = pipeline("fill-mask")#,  model = "xlm-roberta-base")
# model_re.
# model_re.parameters()
nlp = spacy.load('en_core_web_lg')



###########Needed Utilities################
def getWikiPageText(entity):
    
    wiki = wikipediaapi.Wikipedia(
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI
    )
    return wiki.page('{0}'.format(entity))

def cosineSim(x: str, y: str):
    return cosine_similarity(model_embedding.encode(x, show_progress_bar=False).reshape(1, -1), model_embedding.encode(y, show_progress_bar=False).reshape(1, -1))

def extractRelations(sentence, subj, obj, falsePO, bert=False, reverse=False): 
    relations = []
    for sub_subj in subj:
        if sub_subj in sentence:
            head_s = sentence.index(sub_subj)
            head_e = head_s + len(sub_subj)
            tail_s = sentence.index(obj)
            tail_e = tail_s + len(obj)
            
            if bert:
                bestResults = model_BERT(f"{sentence} {sub_subj} <mask> {obj} ")
                # i = np.argmax([cosineSim(x['token_str'], falsePO[0]) for x in bestResults[:2]])# if x['score'] > 0.3])
                # bestResult = bestResults[i]
                result = [sub_subj, [[x['token_str'], x['score']] for x in bestResults], obj]
            else:
                result = [sub_subj,
                            [list(model_re.infer({'text': sentence, 'h': {'pos': (head_s, head_e)}, 't': {'pos': (tail_s, tail_e)}}))],
                            obj]
                if reverse:
                    result = [sub_subj,
                            [list(model_re.infer({'text': sentence, 't': {'pos': (head_s, head_e)}, 'h': {'pos': (tail_s, tail_e)}}))],
                            obj]
            print(result)
                
            relations.append(result)
    return relations

def validateRelations(options, falsePO):
    best = [0, options[0]]
    for option in options:
        for relation in option[1]:
            # print('validating ', f'{relation[0]} {option[2]} with', " ".join(falsePO))
            sim = cosineSim(f'{relation[0]} {option[2]}', " ".join(falsePO))
            if best[0] < sim:
                best = [sim, relation]
    return best

def parseRelation(relation):
    spo = helpers.parseTriple(relation)
        
    pred = spo[1] # assuming that all predicates are camel-case;
    # then, we transform them, like: countryOfOrigin -> country of origin 
    if pred == "type":
        pred = 'is'
    else:
        pattern = re.compile(r'(?<!^)(?=[A-Z])')
        pred = pattern.sub(' ', pred).lower()
    
    obj = spo[2].replace('_', ' ') # TODO: are there any special cases? Like - instead of _?

    return (pred, obj)

def compareClassifiers(sent, subj, obj, falsePO, sentSim):
    confidence = sentSim
    # Calculate for NRE
    nreRelations = extractRelations(sent.text, subj, obj, falsePO) # get best 5 candidates, should we consider more?
    _, nreBestRelation = validateRelations(nreRelations, falsePO)
    print(nreBestRelation, nreRelations)
    print('Best NRE Relation Obtained: ', nreBestRelation)
    print('From NRE Relations', nreRelations, '\n')

    # Calculate for BERT
    bertRelations = extractRelations(sent.text, subj, obj, falsePO, bert=True) # get best 5 candidates, should we consider more?
    __, bertBestRelation = validateRelations(bertRelations, falsePO)
    print('Best BERT Relation Obtained: ', bertBestRelation)
    print('From BERT Relations', bertRelations, '\n')
    print('FALSE PO ',  falsePO)


    # Calculate the similarities and choose the best.
    o1 = cosineSim(obj, falsePO[1])[0]
    o2 = cosineSim(obj, falsePO[1])[0]

    p1 = cosineSim(nreBestRelation[0], falsePO[0])[0]
    p2 = cosineSim(bertBestRelation[0], falsePO[0])[0]

    falsePO = ' '.join(falsePO)
    po1 = cosineSim(f'{nreBestRelation[0]} {obj}', falsePO)[0]
    po2 = cosineSim(f'{bertBestRelation[0]} {obj}', falsePO)[0]
    
    mean1 = np.mean([o1, p1, po1])
    mean2 = np.mean([o2, p2, po2])

    print(mean1, mean2)
    # return {'candidate': sent, 'o': obj, 'falsePO': falsePO, 'similarities': allSimilarities}
    return {
            # [0.2, 0.3, mean1, mean2]
            #  confidence level # how sure are we to add a triple!
            'model':'nre', 
            'mean': mean1, 
            'relation': nreBestRelation,
            'confidence': confidence * po1 
            } if mean1 > mean2 \
        else {
            'model': 'bert',
            'mean': mean2, 
            'relation': bertBestRelation,
            'confidence': confidence * po2 
            }
    # pass
    
def runExamples():
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

    sentSim = cosineSim(s, " ".join(falsePO))[0]

    print(compareClassifiers(nlp(s), subject, bestO, falsePO, sentSim))
    

###########Start extracting################




def getCandidates(sents, subj, falsePO):
    candidates = []
    relaventSents = 0
    for sent in sents:
        for token in sent:
            if token.text in subj and token.dep_ == 'nsubj':
                relaventSents = relaventSents + 1
            # if (token.text == "Borussia" or token.text == "Dortmund") and token.dep_ == "nsubj":
                # similarObjs = [[cosineSim(token.text, falsoObj)[0], token.text] for token in sent]
                # similarObjs.sort(key=itemgetter(0), reverse=True)
                # bestObj = similarObjs[0]    
                # candidates.append([sent, bestObj[0], bestObj[1]]) # selected sentence, similarity score, and the chosen, best object.
                sentSim = cosineSim(sent.text, " ".join(falsePO))[0]
                # getBestobj 
                candidates.append([sent, sentSim]) # selected sentence, similarity score, and the chosen, best object.
    
    candidates.sort(key=itemgetter(1), reverse=True) # sort based on the similarity score between the false object and subject with respect to the sentence.
   
    sentsWithObjects = []
    for (sent, sentSim) in candidates[:5]:
        similarObjs = [[cosineSim(token.text, falsePO[1])[0], token.text] for token in sent]
        similarObjs.sort(key=itemgetter(0), reverse=True)
        bestObj = similarObjs[0]    
        if bestObj[0] > 0.6:
            sentsWithObjects.append([sent, bestObj[0], bestObj[1], sentSim]) # selected sentence, similarity score, and the chosen, best object.
        else:
            print('not included ', sent, bestObj)
    print("Relavent sents: ", relaventSents, 'from ', len(list(sents)))
    return sentsWithObjects

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
def main():
    print('Running main...')
    history = helpers.readPickleBack(fileName)
    # print(cosineSim('Hasan hates mo', 'mo loves hasan'))
    # history = []
    s = time.time()
    for i, run in enumerate(history):
        print(f'Run no. {i}')
        if run:
            triplesToAdd = []
            for game in run['games'].values():
                noHints = game['noHints']
                entity = game['entity'][0]['uri'].rsplit('/', 1)[-1]
                subj = entity.split('_')
                subj.append(" ".join(subj))
                doc = nlp(getWikiPageText(entity).text) # TODO: Consider a more robust setence splitter.
                for relation in noHints: 
                    falsePO = parseRelation(relation)
                    print('\nGet Candidates For: ', subj, falsePO[1])
                    candidates = getCandidates(doc.sents, subj, falsePO)
                    candidates.sort(key=itemgetter(1), reverse=True) # sort based on the similarity score between the false object and subject with respect to the sentence.
                    print('Candidates', candidates)
                    bestCandidates = []
                    for i, (sent, _, obj, sentSim) in enumerate(candidates):
                        print(f'SENTENCE no. {i} ', sent, obj)
                    # for sent in doc.sents:
                        # relations = [extractRelations(s.text, subj, obj) for [s, _, obj] in candidates[:5]][0] # get best 5 candidates, should we consider more?
                        result = compareClassifiers(sent, subj, obj, falsePO, sentSim)
                        bestCandidates.append(result)
                    
                    if bestCandidates:
                        bestCandidate = max(bestCandidates, key=lambda x: x['confidence'])
                        print('best candidates ', bestCandidates)
                        print('FINAL CAND. ', bestCandidate)
                        if bestCandidate['confidence'] > 0.30:
                            relation.pop(0)
                            relation.insert(0, game['entity'][0])
                            triplesToAdd.append(relation)
                    # break
                break
            # print(run['noHints'])
            break
        else:
            print('empty', run)
    for t in triplesToAdd:
        print('\nADD the following: ', t, '\n')

    curr_time = (time.time() - s) * 1000
    print(curr_time)
    # falseRelations = [[helpers.parseTriple(noHints[i])[1],helpers.parseTriple(noHints[i])[2]] for i in range(len(noHints))]
    # 

parser = ArgumentParser()

parser.add_argument("-f", "--file-name",
                    dest="fileName",
                    help="File name to read from (Default: tournament_runs.pkl)",
                    type=str,
                    default="tournament_runs.pkl")

parser.add_argument("-t", "--test",
                    dest="test",
                    help="Run the test&examples",
                    type=bool,
                    default=False)

options = parser.parse_args()
fileName = options.fileName
test = options.test

if __name__ == '__main__':
    if test:
        runExamples()
    else:
        main()