import wikipediaapi
import re
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from operator import itemgetter
from util import helpers


def getWikiPageText(entity):
    
    wiki = wikipediaapi.Wikipedia(
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI
    )
    return wiki.page('{0}'.format(entity))

def parseRelation(relation, key='value'):
    spo = helpers.parseTriple(relation, key)
        
    pred = spo[1] # assuming that all predicates are camel-case;
    # then, we transform them, like: countryOfOrigin -> country of origin 
    if pred == "type":
        pred = 'is'
    else:
        pattern = re.compile(r'(?<!^)(?=[A-Z])')
        pred = pattern.sub(' ', pred).lower()
    
    obj = spo[2].replace('_', ' ') # TODO: are there any special cases? Like - instead of _?

    return (pred, obj)

model_embedding = SentenceTransformer('all-mpnet-base-v2')
model_embedding.cuda()

def cosineSim(x: str, y: str):
    return cosine_similarity(model_embedding.encode(x, show_progress_bar=False).reshape(1, -1), model_embedding.encode(y, show_progress_bar=False).reshape(1, -1))

def getCandidates(sents, subj, falsePO, acceptenceLevel=0.6):
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
        if bestObj[0] > acceptenceLevel:
            sentsWithObjects.append([sent, bestObj[0], bestObj[1], sentSim]) # selected sentence, similarity score, and the chosen, best object.
    #     else:
    #         print('not included ', sent, bestObj)
    # print("Relavent sents: ", relaventSents, 'from ', len(list(sents)))
    return sentsWithObjects
    # 05348372279
