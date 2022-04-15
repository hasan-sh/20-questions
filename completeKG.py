from util import helpers
import wikipediaapi
import spacy
import re
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import opennre
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from operator import itemgetter

from util import helpers

# !pip install wikipedia-api spacy transformers sentence_transformers pytest
# !pip3 uninstall torch torchvision torchaudio #--extra-index-url https://download.pytorch.org/whl/cu113
# !python -m spacy download en_core_web_lg
# pip install git+https://github.com/thunlp/OpenNRE



###########Needed Utilities################
def getWikiPageText(entity):
    
    wiki = wikipediaapi.Wikipedia(
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI
    )
    return wiki.page('{0}'.format(entity))

def cosineSim(x, y):
    return cosine_similarity(model_embedding.encode(x).reshape(1, -1), model_embedding.encode(y).reshape(1, -1))

def extractRelations(sentence, subj, obj, reverse=False): 
    relations = []
    for sub_subj in subj:
        if sub_subj in sentence:
            head_s = sentence.index(sub_subj)
            head_e = head_s + len(sub_subj)
            tail_s = sentence.index(obj)
            tail_e = tail_s + len(obj)
            
            result = model_re.infer({'text': sentence, 'h': {'pos': (head_s, head_e)}, 't': {'pos': (tail_s, tail_e)}})
            if reverse:
                result = model_re.infer({'text': sentence, 't': {'pos': (head_s, head_e)}, 'h': {'pos': (tail_s, tail_e)}})
                
            relations.append((sub_subj, result, obj))
    return relations

def validateRelations(relations, falsePO):
    best = (0, relations[0])
    for relation in relations:
        sim = cosineSim(f'{relation[1][0]} {relation[2]}', falsePO)
        print(relation)
        if best[0] < sim:
            best = (sim, relation)
    return best

def compareClassifiers():
    pass
    
def runExamples():
    s = 'The Los Angeles Lakers is a good team. They are an American professional basketball team based in Los Angeles.'
    # s = 'The United States of America (U.S.A. or USA), commonly known as the United States (U.S. or US) or simply America, is a country primarily located in North America.'
    subject = ['Los Angeles Lakers', 'Los Angeles', 'Lakers', 'Dortmund'] # TODO: use PoS on the subject.
    # subject = ['United States', 'States'] # TODO: use PoS on the subject.
    falseO = 'American'
    # falseO = 'North America'

    relations = extractRelations(s, subject, falseO)
    # print(relations)
    return validateRelations(relations, "country of origin United States")
    

###########Start extracting################


# TODO: step 1 get entities and no hints
entity = [{'type': 'uri', 'uri': 'http://yago-knowledge.org/resource/Borussia_Dortmund'}][0]['uri'].rsplit('/', 1)[-1]
noHints = [[{'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'type': 'literal', 'value': '56903', 'uri': '56903', 'prefix_entity': "'56903'"}, {'type': 'uri', 'value': 'countryOfOrigin', 'uri': 'http://schema.org/countryOfOrigin', 'prefix': 'http://schema.org/', 'prefix_entity': 'x0:countryOfOrigin'}, {'type': 'uri', 'value': 'United_States', 'uri': 'http://yago-knowledge.org/resource/United_States', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:United\\_States'}], [{'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'type': 'literal', 'value': '21762', 'uri': '21762', 'prefix_entity': "'21762'"}, {'type': 'uri', 'value': 'countryOfOrigin', 'uri': 'http://schema.org/countryOfOrigin', 'prefix': 'http://schema.org/', 'prefix_entity': 'x0:countryOfOrigin'}, {'type': 'uri', 'value': 'India', 'uri': 'http://yago-knowledge.org/resource/India', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:India'}], [{'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'type': 'literal', 'value': '11454', 'uri': '11454', 'prefix_entity': "'11454'"}, {'type': 'uri', 'value': 'countryOfOrigin', 'uri': 'http://schema.org/countryOfOrigin', 'prefix': 'http://schema.org/', 'prefix_entity': 'x0:countryOfOrigin'}, {'type': 'uri', 'value': 'United_Kingdom', 'uri': 'http://yago-knowledge.org/resource/United_Kingdom', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:United\\_Kingdom'}], [{'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'type': 'literal', 'value': '8714', 'uri': '8714', 'prefix_entity': "'8714'"}, {'type': 'uri', 'value': 'countryOfOrigin', 'uri': 'http://schema.org/countryOfOrigin', 'prefix': 'http://schema.org/', 'prefix_entity': 'x0:countryOfOrigin'}, {'type': 'uri', 'value': 'France', 'uri': 
'http://yago-knowledge.org/resource/France', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:France'}], [{'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'type': 'literal', 'value': '7149', 'uri': '7149', 'prefix_entity': "'7149'"}, {'type': 'uri', 'value': 'countryOfOrigin', 'uri': 'http://schema.org/countryOfOrigin', 'prefix': 'http://schema.org/', 'prefix_entity': 'x0:countryOfOrigin'}, {'type': 'uri', 'value': 'Germany', 'uri': 'http://yago-knowledge.org/resource/Germany', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:Germany'}], [{'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'type': 'literal', 'value': '4030', 'uri': '4030', 'prefix_entity': "'4030'"}, {'type': 'uri', 'value': 'countryOfOrigin', 'uri': 'http://schema.org/countryOfOrigin', 'prefix': 'http://schema.org/', 'prefix_entity': 'x0:countryOfOrigin'}, {'type': 'uri', 'value': 'Canada', 'uri': 'http://yago-knowledge.org/resource/Canada', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:Canada'}], [{'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'type': 'literal', 'value': '3855', 'uri': '3855', 'prefix_entity': "'3855'"}, {'type': 'uri', 'value': 'countryOfOrigin', 'uri': 'http://schema.org/countryOfOrigin', 'prefix': 'http://schema.org/', 'prefix_entity': 'x0:countryOfOrigin'}, {'type': 'uri', 'value': 'Japan', 'uri': 'http://yago-knowledge.org/resource/Japan', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:Japan'}], [{'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'type': 'literal', 'value': '3473', 'uri': '3473', 'prefix_entity': "'3473'"}, {'type': 'uri', 'value': 'type', 'uri': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'prefix': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#', 'prefix_entity': 'x2:type'}, {'type': 'uri', 'value': 'Movie', 'uri': 'http://schema.org/Movie', 'prefix': 'http://schema.org/', 'prefix_entity': 'x0:Movie'}], [{'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'type': 'literal', 'value': '2768', 'uri': '2768', 'prefix_entity': "'2768'"}, {'type': 'uri', 'value': 'countryOfOrigin', 'uri': 'http://schema.org/countryOfOrigin', 'prefix': 'http://schema.org/', 'prefix_entity': 'x0:countryOfOrigin'}, {'type': 'uri', 'value': 'Australia', 'uri': 'http://yago-knowledge.org/resource/Australia', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:Australia'}], [{'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'type': 
'literal', 'value': '1787', 'uri': '1787', 'prefix_entity': "'1787'"}, {'type': 'uri', 'value': 'countryOfOrigin', 'uri': 'http://schema.org/countryOfOrigin', 'prefix': 'http://schema.org/', 'prefix_entity': 'x0:countryOfOrigin'}, {'type': 'uri', 'value': 'Soviet_Union', 'uri': 'http://yago-knowledge.org/resource/Soviet_Union', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:Soviet\\_Union'}], [{'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'type': 'literal', 'value': '183', 'uri': '183', 'prefix_entity': "'183'"}, {'type': 'uri', 'value': 'nationality', 'uri': 'http://schema.org/nationality', 'prefix': 'http://schema.org/', 'prefix_entity': 'x0:nationality'}, {'type': 'uri', 'value': 'India', 'uri': 'http://yago-knowledge.org/resource/India', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:India'}], [{'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'type': 'literal', 'value': '155', 'uri': '155', 'prefix_entity': "'155'"}, {'type': 'uri', 'value': 'nationality', 'uri': 'http://schema.org/nationality', 'prefix': 'http://schema.org/', 'prefix_entity': 'x0:nationality'}, {'type': 'uri', 'value': 'Canada', 'uri': 'http://yago-knowledge.org/resource/Canada', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:Canada'}], [{'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'type': 'literal', 'value': '36', 'uri': '36', 'prefix_entity': "'36'"}, {'type': 'uri', 'value': 'hasOccupation', 'uri': 'http://schema.org/hasOccupation', 'prefix': 'http://schema.org/', 'prefix_entity': 'x0:hasOccupation'}, {'type': 'uri', 'value': 'Film_producer', 'uri': 'http://yago-knowledge.org/resource/Film_producer', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:Film\\_producer'}], [{'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'type': 'literal', 'value': '21', 'uri': '21', 'prefix_entity': "'21'"}, {'type': 'uri', 'value': 'hasOccupation', 'uri': 'http://schema.org/hasOccupation', 'prefix': 'http://schema.org/', 'prefix_entity': 'x0:hasOccupation'}, {'type': 'uri', 'value': 'Screenwriter', 'uri': 'http://yago-knowledge.org/resource/Screenwriter', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:Screenwriter'}], [{'datatype': 'http://www.w3.org/2001/XMLSchema#integer', 'type': 'literal', 'value': '20', 'uri': '20', 'prefix_entity': "'20'"}, {'type': 'uri', 'value': 'hasOccupation', 'uri': 'http://schema.org/hasOccupation', 'prefix': 'http://schema.org/', 'prefix_entity': 'x0:hasOccupation'}, {'type': 'uri', 'value': 'Film_director', 'uri': 'http://yago-knowledge.org/resource/Film_director', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:Film\\_director'}]]

history = helpers.readPickleBack('tournament_output.pkl')
# print(history[1])
for tournamentRun in history[:1]:
    print(type(tournamentRun))
    for game in tournamentRun['games']:
        print(game['noHints'])
        break

    # for  in i:
#         print(i['noHints'])
#         break

# falseRelations = [[helpers.parseTriple(noHints[i])[1],helpers.parseTriple(noHints[i])[2]] for i in range(len(noHints))]
# # classifier = pipeline("fill-mask")#,  model = "xlm-roberta-base")

# model_embedding = SentenceTransformer('all-mpnet-base-v2')
# model_re = opennre.get_model('wiki80_cnn_softmax')

# nlp = spacy.load('en_core_web_lg')

# doc = nlp(p_wiki.text) # TODO: Consider a more robust setence splitter.