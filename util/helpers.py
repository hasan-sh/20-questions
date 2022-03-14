import importlib

# def parseTriple(triple):
#     ''' Makes a human readable string out of a single triple of URI's'''
#     s = triple[0].split('/')[-1]
#     p = triple[1].split('/')[-1].split('#')[-1]
#     o = triple[2].split('/')[-1]
#     return (s, p, o)

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
    
    """
    s = ''
    for hint in yesHints: 
        (_, p, o) = hint
        s += f"\nfilter (?p != <{p['value']}> || ?o != "
        if o['type'] == "literal":
            s += f"\"{o['value']}{o['xml:lang']}\")"
        else:
            s += f"<{o['value']}>)"
    
    for hint in noHints: 
        (_, p, o) = hint
        s += f"\nfilter not exists {{ ?s <{p['value']}> "
        if o['type'] == "literal":
            s += f"\"{o['value']}{o['xml:lang']}\" . }}"
        else:
            s += f"<{o['value']}> . }}"
    return s

def load_bot(name):
    """
    name: The folder name of the bot.
    """
    path = f'bots.{name}.bot'
    module = importlib.import_module(path)
    bot = getattr(module, f'{name}Bot')
    return bot