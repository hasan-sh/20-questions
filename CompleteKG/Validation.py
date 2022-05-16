from operator import itemgetter
from numpy import place, argmax
import requests
from CompleteKG.helpers import parseRelation, cosineSim
from qwikidata.sparql import (get_subclasses_of_item,
                              return_sparql_query_results)
import time
from util.api import API

class Validation:
    def __init__(self) -> None:
        self.wikiResults = {}
    # entity = 'Taylor_Swift'
    # entity = 'Borussia_Dortmund'
    def getWikidataId(self, entity):
        # from wikipedia api!
        result = requests.get('https://en.wikipedia.org/w/api.php?action=query&prop=pageprops&ppprop=wikibase_item&format=json&redirects=1&titles='+entity)
        result = result.json()
        page = result.get('query').get('pages')#.get('pageprops').get('wikibase_item'))
        page = list(page.values())
        url='https://query.wikidata.org/sparql'

        wikidataID = page[0].get('pageprops').get('wikibase_item')
        # print(f'Wikidata URI: {url}/{wikidataID} \nEntity: {entity}')
        return wikidataID

    def validate(self, entityPossibleRelations, acceptenceLevel=0.6):
        s = time.time()
        validated = {}
        url='https://query.wikidata.org/sparql'
        api = API(url)
        print(entityPossibleRelations.keys()) 
        for id in entityPossibleRelations.keys():
            if self.wikiResults.get(id):
                result = self.wikiResults[id]
            else:
                print(f'Wikidata id: {id} ')
                predicatesQuery = f'''\
                SELECT ?p ?propLabel ?oLabel\
                WHERE\
                {{
                    wd:{id} ?p ?o .
                    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}
                    ?prop wikibase:directClaim ?p .
                }}
                '''
                print(predicatesQuery)
                result = return_sparql_query_results(predicatesQuery)
                result = api.parseJSON(result, variables=[['p', 'propLabel', 'oLabel']])
                # result=[]
                self.wikiResults[id] = result

            allRelations = entityPossibleRelations[id]
            correctTriples = []
            validated[id] = {
                'all': allRelations
            }
            # print(id, allRelations)
            for relation in allRelations:
                validated[id]['entity'] = relation.get('entity')
                parsedTriple = parseRelation(relation.get('triple'), 'uri')
                print(parsedTriple)
                modelsPredicate = relation.get('candidate').get('modelsRelation')[0]
                modelsObject = relation.get('candidate').get('obj')
                best = {}
                for (p, pLabel, oLabel) in result:
                    pSim = max(cosineSim(pLabel.get('value'), parsedTriple[0])[0], cosineSim(pLabel.get('value'), modelsPredicate)[0])[0]
                    oSim = max(cosineSim(oLabel.get('value'), parsedTriple[1])[0], cosineSim(oLabel.get('value'), modelsObject)[0])[0]
                    poSim = cosineSim(f'{pLabel.get("value")} {oLabel.get("value")}', f'{parsedTriple[0]} {parsedTriple[1]}')[0]
                    
                    # if (pSim > 0.5 or oSim > 0.5) and min(pSim, oSim) > 0.3:
                    if poSim > acceptenceLevel:
                        print('\n')
                        print(pSim, oSim, poSim)
                        print( pLabel.get('value'), oLabel.get('value'))
                        print( parsedTriple[0], parsedTriple[1])
                        print( modelsPredicate, modelsObject)
                        print('\n')
                        bestResult = [(p.get('value'), pLabel.get('value'), oLabel.get('value')), relation, poSim]
                        if best.get(p.get('value')):
                            best[p.get('value')].append(bestResult)#max(pSim, oSim)[0]))
                        else:
                            best[p.get('value')] = [bestResult]
                if best:
                    best = list(best.values())[0]
                    best.sort(key=itemgetter(-1), reverse=True)
                    correctTriples.append(best[0])
                        # print('\n best added', best[0], '\n')
            validated[id]['correct'] = correctTriples
            print('added now validated', id, len(validated[id]['all']), len(validated[id]['correct']))
                # print('\n')

        curr_time = (time.time() - s) * 1000
        print('it took: ', curr_time)
        return validated # correctTriples, allRelations 
            

# TEST

# triples = { 'Q26876': [
#     ({'candidate': {'sent': 'Besides longtime collaborator Jack Antonoff, Swift worked with new producers Louis Bell, Frank Dukes, and Joel Little.', 'obj': 'producers', 'model': 'nre', 'modelsRelation': ['occupation', 0.16862252354621887]},  'triple': [{'type': 'uri', 'uri': 'http://yago-knowledge.org/resource/Taylor_Swift'}, {'type': 'uri', 'value': 'hasOccupation', 'uri': 'http://schema.org/hasOccupation', 'prefix': 'http://schema.org/', 'prefix_entity': 'x2:hasOccupation'}, {'type': 'uri', 'value': 'Film_producer', 'uri': 'http://yago-knowledge.org/resource/Film_producer', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:Film\\_producer'}], 'entity': 'Taylor_Swift'}, 'Q26876'),
    
#     ({'candidate': {'sent': 'Describing her omnipresence, The Ringer writer Kate Knibbs said Swift is not just a pop act but "a musical biosphere unto herself", having achieved the kind of success "that turns a person into an institution, into an inevitability.', 'obj': 'writer', 'model': 'nre', 'modelsRelation': ['screenwriter', 0.8141699433326721]},  'triple': [{'type': 'uri', 'uri': 'http://yago-knowledge.org/resource/Taylor_Swift'}, {'type': 'uri', 'value': 'hasOccupation', 'uri': 'http://schema.org/hasOccupation', 'prefix': 'http://schema.org/', 'prefix_entity': 'x2:hasOccupation'}, {'type': 'uri', 'value': 'Screenwriter', 'uri': 'http://yago-knowledge.org/resource/Screenwriter', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:Screenwriter'}], 'entity': 'Taylor_Swift'}, 'Q26876'),
    
#     ({'candidate': {'sent': '"From 2014 to 2018, Swift collaborated with director Joseph Kahn on eight music videos—four each from her albums 1989 and Reputation.', 'obj': 'director', 'model': 'nre', 'modelsRelation': ['occupation', 0.8510352969169617]},  'triple': [{'type': 'uri', 'uri': 'http://yago-knowledge.org/resource/Taylor_Swift'}, {'type': 'uri', 'value': 'hasOccupation', 'uri': 'http://schema.org/hasOccupation', 'prefix': 'http://schema.org/', 'prefix_entity': 'x2:hasOccupation'}, {'type': 'uri', 'value': 'Film_director', 'uri': 'http://yago-knowledge.org/resource/Film_director', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:Film\\_director'}], 'entity': 'Taylor_Swift'}, 'Q26876'),
    
#     ({'candidate': {'sent': 'At age nine, Swift became interested in musical theater and performed in four Berks Youth Theatre Academy productions.', 'obj': 'theater', 'model': 'bert', 'modelsRelation': [' enjoys', 0.12505848705768585]},  'triple': [{'type': 'uri', 'uri': 'http://yago-knowledge.org/resource/Taylor_Swift'}, {'type': 'uri', 'value': 'hasOccupation', 'uri': 'http://schema.org/hasOccupation', 'prefix': 'http://schema.org/', 'prefix_entity': 'x2:hasOccupation'}, {'type': 'uri', 'value': 'Stage_actor', 'uri': 'http://yago-knowledge.org/resource/Stage_actor', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:Stage\\_actor'}], 'entity': 'Taylor_Swift'}, 'Q26876'),
    
#     ({'candidate': {'sent': 'Swift was around 12 years old, computer repairman and local musician Ronnie Cremer taught her to play guitar.', 'obj': 'guitar', 'model': 'bert', 'modelsRelation': [' plays', 0.5662645697593689]}, 'triple': [{'type': 'uri', 'uri': 'http://yago-knowledge.org/resource/Taylor_Swift'}, {'type': 'uri', 'value': 'hasOccupation', 'uri': 'http://schema.org/hasOccupation', 'prefix': 'http://schema.org/', 'prefix_entity': 'x2:hasOccupation'}, {'type': 'uri', 'value': 'Guitarist', 'uri': 'http://yago-knowledge.org/resource/Guitarist', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:Guitarist'}], 'entity': 'Taylor_Swift'}, 'Q26876'),
    
#     ({'candidate': {'sent': "Swift was 2020's highest-paid musician in the U.S., and highest-paid solo musician worldwide.", 'obj': 'musician', 'model': 'nre', 'modelsRelation': ['occupation', 0.7819189429283142]}, 'triple': [{'type': 'uri', 'uri': 'http://yago-knowledge.org/resource/Taylor_Swift'}, {'type': 'uri', 'value': 'hasOccupation', 'uri': 'http://schema.org/hasOccupation', 'prefix': 'http://schema.org/', 'prefix_entity': 'x2:hasOccupation'}, {'type': 'uri', 'value': 'Pianist', 'uri': 'http://yago-knowledge.org/resource/Pianist', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:Pianist'}], 'entity': 'Taylor_Swift'}, 'Q26876'),
    
#     ({'candidate': {'sent':  '2004–2008: Career beginnings and first album In Nashville, Swift worked with experienced Music Row songwriters such as Troy Verges, Brett Beavers, Brett James, Mac McAnally, and the Warren Brothers and formed a lasting working relationship with Liz Rose.', 'obj': 'songwriters', 'model': 'bert', 'modelsRelation': ["'s", 0.02959771826863289]},  'triple': [{'type': 'uri', 'uri': 'http://yago-knowledge.org/resource/Taylor_Swift'}, {'type': 'uri', 'value': 'hasOccupation', 'uri': 'http://schema.org/hasOccupation', 'prefix': 'http://schema.org/', 'prefix_entity': 'x2:hasOccupation'}, {'type': 'uri', 'value': 'Songwriter', 'uri': 'http://yago-knowledge.org/resource/Songwriter', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:Songwriter'}], 'entity': 'Taylor_Swift'}, 'Q26876'),
    
#     ({'candidate': {'sent': 'Folklore won Album of the Year at the 63rd Annual Grammy Awards, making Swift the first woman in history to win the award three times.', 'obj': 'Grammy', 'model': 'bert', 'modelsRelation': [' wins', 0.8025652170181274]},  'triple': [{'type': 'uri', 'uri': 'http://yago-knowledge.org/resource/Taylor_Swift'}, {'type': 'uri', 'value': 'award', 'uri': 'http://schema.org/award', 'prefix': 'http://schema.org/', 'prefix_entity': 'x2:award'}, {'type': 'uri', 'value': 'MusiCares_Person_of_the_Year', 'uri': 'http://yago-knowledge.org/resource/MusiCares_Person_of_the_Year', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:MusiCares\\_Person\\_of\\_the\\_Year'}], 'entity': 'Taylor_Swift'}, 'Q26876')
# ]}
 
# id = getWikidataId(entity)
# print(id, entity)
# validate(triples)
#     {'candidate': 
#         {'sent': 'Describing her omnipresence, The Ringer writer Kate Knibbs said Swift is not just a pop act but "a musical biosphere unto herself", having achieved the kind of success "that turns a person into an institution, into an inevitability.', 
#         'obj': 'writer',
#         'model': 'nre', 
#         'modelsRelation': ['screenwriter', 0.8141699433326721], 
#         'confidence': 0.22276439,
#         }, 
#         'triple': [{'type': 'uri', 'uri': 'http://yago-knowledge.org/resource/Taylor_Swift'}, 
#             {'type': 'uri', 'value': 'hasOccupation', 'uri': 'http://schema.org/hasOccupation', 'prefix': 'http://schema.org/', 'prefix_entity': 'x2:hasOccupation'}, 
#             {'type': 'uri', 'value': 'Screenwriter', 'uri': 'http://yago-knowledge.org/resource/Screenwriter', 'prefix': 'http://yago-knowledge.org/resource/', 'prefix_entity': 'x1:Screenwriter'}]
#     }
# , id)])



