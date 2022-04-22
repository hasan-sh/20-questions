import requests
from util.api import API
# import wikipediaapi

# wiki = wikipediaapi.Wikipedia(
#     language='en',
#     extract_format=wikipediaapi.ExtractFormat.WIKI
# )

entity = 'Taylor_Swift'
entity = 'Borussia_Dortmund'
def getWikidataId(entity):
    # from wikipedia api!
    result = requests.get('https://en.wikipedia.org/w/api.php?action=query&prop=pageprops&ppprop=wikibase_item&format=json&redirects=1&titles='+entity)
    result = result.json()
    page = result.get('query').get('pages')#.get('pageprops').get('wikibase_item'))
    page = list(page.values())
    url='https://query.wikidata.org/sparql'

    wikidataID = page[0].get('pageprops').get('wikibase_item')
    # print(f'Wikidata URI: {url}/{wikidataID} \nEntity: {entity}')
    return wikidataID


def validate(wikidataIDs, entity):
    correctTriples = []
    url='https://query.wikidata.org/sparql'
    api = API(url)
    for id in wikidataIDs:

        print(f'Wikidata id: {id} \nEntity: {entity}')


        query = f'''\
        SELECT *\
        WHERE\
        {{
            wd:{id} ?p ?o .
            #SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}

        }}
        '''
        """
        TODO: 
            - check the properties dynamically,
            - apply cosine sim for that one and the relation to add,
            - and then try to conclude whether to add it or not!
        """
        print(query)
        result = api.queryKG(query)
        for row in result["results"]["bindings"]:
            for keys in row:
                print(keys, row)
        # result = api.parseJSON(result)
        # print(result)