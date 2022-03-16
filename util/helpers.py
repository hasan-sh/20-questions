import importlib
# import api

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

"""
Q1:
    gets the most common p o.
Intermediate step:
    choose the first one of p o combination = result1
Q2:
    gets the most common p1 o1 of the result1
Final:
    choose the first one of p1 o1 combination = final

Final is chosen, pose "final" as a question.
"""

q1 = """
SELECT distinct ?p ?o
        (count(concat(str(?p), str(?o))) as ?poCount)
WHERE {
  ?s ?p ?o.
}
GROUP BY ?p ?o
ORDER BY DESC (?poCount )
limit 10000
"""

# qres = []
# result1 = qres[0]

# q2 = """
# SELECT distinct {result[1]} {result[2]} 
#         (count(concat(str({result[1]}), str({result[2]}))) as ?poCount)
# WHERE {
#   ?s {result[1]} {result[2]}.
# }
# GROUP BY {result[1]} {result[2]}
# ORDER BY DESC (?poCount )
# limit 10000
# """

# qres1 = []
# final = qres1[0]


# question = final[0] # Tada!!!


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