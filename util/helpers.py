import importlib
# import api

# def parseTriple(triple):
#     ''' Makes a human readable string out of a single triple of URI's'''
#     s = triple[0].split('/')[-1]
#     p = triple[1].split('/')[-1].split('#')[-1]
#     o = triple[2].split('/')[-1]
#     return (s, p, o)

def parsePrefixes(triple):
    ''' Retrieves all prefixes out of a single triple'''
    result = ['#'.join(v.get('value').split('#')[:-1]) + '#'
                if '#' in v.get('value')
                else '/'.join(v.get('value').split('/')[:-1])+'/'
                for v in triple if v.get('type') == 'uri']
    return result if result else triple[0].get('value')


def parseTriple(triple):
    ''' Makes a human readable string out of a single triple of URI's'''
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
            s += f"\"{o['value']}"
            if o.get('xml:lang'): # only if there's lang we add it.
                s += f"{o['xml:lang']}"
            s += '". }}'
        else:
            s += f"{o['prefix_entity']})"

    for hint in noHints:
        (_, p, o) = hint
        s += f"\nfilter not exists {{ ?s {p['prefix_entity']} "
        if o['type'] == "literal":
            s += f"\"{o['value']}"
            if o.get('xml:lang'):
                s += f"{o['xml:lang']}"
            s += '". }'
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
def rescursive_query(p, o, api, depth=0):
    query = f"""
    SELECT distinct {p} {o} 
            (count(concat(str({p}), str({o}))) as ?poCount)
    WHERE {{
    ?s {p} {o}.
    }}
    GROUP BY {p} {o}
    ORDER BY DESC (?poCount )
    limit 10000
    """
    # make query
    # select result
    # print('before' , query)
    qres = api.queryTest(query=query)
    qres = api.parseJSON(qres, [['p', 'o', '?poCount']])
    # print(qres)
    result = qres[0]
    if depth > 0:
        return  rescursive_query(result[0]['value'], result[1]['value'], depth-1)
    return result