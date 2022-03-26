import importlib
import re, string
from reprlib import recursive_repr
import numpy as np
from matplotlib.pyplot import hist
import random

# def parseTriple(triple):
#     ''' Makes a human readable string out of a single triple of URI's'''
#     s = triple[0].split('/')[-1]
#     p = triple[1].split('/')[-1].split('#')[-1]
#     o = triple[2].split('/')[-1]
#     return (s, p, o)

def createLabel(s):
    return s['value'].replace('_',' ')
    
def escapeCharacters(s):
    return re.sub(r"([%s])"%(string.punctuation.replace(":", "")),    r"\\\1", s)

def parsePrefixes(triple):
    ''' Retrieves all prefixes out of a single triple'''
    result = ['#'.join(v.get('value').split('#')[:-1]) + '#'
                if '#' in v.get('value')
                else '/'.join(v.get('value').split('/')[:-1])+'/'
                for v in triple if v.get('type') == 'uri']
    if not result:
        print('NO result', result, triple)
    return result#if result else triple[0].get('value')


def parseTriple(triple):
    ''' Makes a human readable string out of a single triple of URI's'''
    if type(triple) == 'tuple':    
        print(triple)
    return [v.get('value').split('/')[-1].split('#')[-1] for v in triple]


def parseGraph(g):
    ''' Transform all triples in a graph to human readable strings.
    Return: list of the triples (NOT GRAPH)'''
    parsedGraph = []
    for triple in g:
        s = triple[0].split('/')[-1]
        p = triple[1].split('/')[-1].split('#')[-1]
        o = triple[2].split('/')[-1]
        parsedGraph.append((s, p, o))
    return parsedGraph


def addFilterSPARQL(yesHints = [], noHints = []):
    """
    Returns a string object consisting of all yesHints and noHints. Each time a question is asked, the string object is extended with the used (o,p)
    The number of total hints is equal to the number of questions asked so far.

    """
    s = ''
    for hint in yesHints:
        (_, p, o) = hint
        s += f"\nfilter (?p != {p['prefix_entity']} || ?o != "
        if o['type'] == "literal":
            s += f"\"{o['value']}\""
            if o.get('xml:lang'): # only if there's lang we add it.
                s += f"@{o['xml:lang']}"
            s += '. }}'
        else:
            s += f"{o['prefix_entity']})"

    for hint in noHints:
        (_, p, o) = hint
        s += f"\nfilter not exists {{ ?s {p['prefix_entity']} "
        if o['type'] == "literal":
            s += f"\"{o['value']}\""
            if o.get('xml:lang'):
                s += f"@{o['xml:lang']}"
            s += '. }'
        else:
            s += f"{o['prefix_entity']} . }}"
    return s


def load_bot(name):
    """
    name: The folder name of the bot.
    """
    path = f'bots.{name}.bot'
    module = importlib.import_module(path)
    bot = getattr(module, f'{name}Bot')
    return bot


# api = api.API()
# this is a first step to entropy
# However, this actually finds the most common p o combinations, recursively

# rescursive_query([Hisham, a, Human])
def rescursiveQuery(state, split=0.5, depth=0):
    api = state.api
    prefixes = '\n'.join(api.prefixes)
    query = f"""
    {prefixes}
    SELECT distinct ?p ?o 
            (count(?s) as ?poCount)
    WHERE {{
    ?s ?p ?o ;
        {';'.join([" {} {}".format(p['prefix_entity'], o['prefix_entity']) for (_, p, o) in state.yesHints])} .
        {addFilterSPARQL(yesHints=state.yesHints, noHints=state.noHints)}    
    }}
    GROUP BY ?p ?o
    ORDER BY DESC (?poCount)
    """
    if not state.yesHints:
        query = f"""
        {prefixes}
        SELECT distinct ?p ?o (count(?s) as ?poCount)
        WHERE {{?s ?p ?o .
        {addFilterSPARQL(noHints=state.noHints)} }}
        GROUP BY ?p ?o
        having(?poCount > 10) 
        ORDER BY DESC (?poCount)
        """
    qres = api.queryKG(query=query)
    qres = api.parseJSON(qres, [['poCount', 'p', 'o']])
    result = qres # select based on the split
    totalCount = getCurrentCount(state, api)
    a = np.array([int(x[0]['value']) for x in result])
    if np.all(a == 1): # This means that the bot found one specific subject, and there is only one label!
        labels = list(filter(lambda x: x[1]['value'] == 'label', qres))
        print('Found only labels!', query)
        return random.choice(labels)
    # print('count ', totalCount )
    
    best = min(qres, key=lambda x: abs(int(x[0]['value']) - int(totalCount) * split))
    if depth > 0:
        return  rescursiveQuery(state.yesHints, depth-1)#result[0]['value'], result[1]['value'], depth-1)
    return best

def getCurrentCount(state, api):
    prefixes = '\n'.join(api.prefixes)
    query = f"""
    {prefixes}

    SELECT (count(?s) as ?TotalCount)
    WHERE {{
    ?s {';'.join([" {} {}".format(p['prefix_entity'], o['prefix_entity']) for (_, p, o) in state.yesHints])} .
    }}
    """
    
    if not state.yesHints:
        query = f"""
        SELECT (count(?s) as ?TotalCount)
        WHERE {{?s ?p ?o .}}
        """
    qres = api.queryKG(query=query)
    qres = api.parseJSON(qres, [['TotalCount']])
    return qres[0][0]['value']