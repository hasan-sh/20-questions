import importlib
import re, string
import numpy as np
import random
import pickle

"""
Contains multiple functions that serve to assist the game.

Methods
-------
createLabel(s)
    Meant to create labels. Takes parsed uri as input, thus entity['value'].

escapeCharacters(s)
    Meant to escape specific punctuations when creating the prefixed entity.

parsePrefixes(triple)
    Retrieves all prefixes out of a single triple.

parseTriple(triple)
    Makes a human readable string out of a single triple of URI's.

parseGraph(g)
    Transform all triples in a graph to human readable strings.

addFilterSPARQL(yesHints, noHints)
    Returns a string object consisting of all yesHints and noHints thats could be used directly into a SPARQL query.

load_Bot(name)
    Takes the name of the bot and creates an object to intialize the bot.

rescursiveQuery(state, split, depth, lastKnownAnswer)
    Used by the entropy bot, makes a query which retrieves the po's and thier counts.

getCurrentCount(state)
    Used by entropy bot, retrieves the count of po's given certain state

readPickleBack(filename)
    Reads the pickle file that stores all informations about the runs.

retrieveName(predicate, question, state)
    ??
"""

def createLabel(s):
    ''' 
    Meant to create labels. Takes parsed uri as input, thus entity['value'] 
    
    Parameters 
    ----------
    s : str
        Parsed uri of the entity.

    Returns
    -------
    The parsed uri, without underscores.
    
    '''
    return s['value'].replace('_',' ')
    
def escapeCharacters(s):
    ''' 
    Meant to escape specific punctuations when creating the prefixed entity 
    
    Parameters 
    ----------
    s : str
        Parsed uri of the entity.

    Returns
    -------
    A prefixed entity without specific puntuations?
    '''
    return re.sub(r"([%s])"%(string.punctuation.replace(":", "")),    r"\\\1", s)

def parsePrefixes(triple):
    ''' 
    Retrieves all prefixes out of a single triple

    Parameters 
    ----------
    triple : list
        A list containing the uri's of a triple. 

    Returns
    -------
    ?
    
    '''
    result = ['#'.join(v.get('value').split('#')[:-1]) + '#'
                if '#' in v.get('value')
                else '/'.join(v.get('value').split('/')[:-1])+'/'
                for v in triple if v.get('type') == 'uri']
    if not result:
        print('NO result', result, triple)
    return result 

def parseTriple(triple):
    ''' 
    Makes a human readable string out of a single triple of URI's
    
    Parameters 
    ----------
    triple : list
        A list containing the uri's of a triple. 

    Returns
    ---
    A list of triples, parsed to be human readable.
    '''
    res = []
    for t in triple:
        if type(t.get('value')) != int:
            # print(type(t))
            res.append(t.get('value').split('/')[-1].split('#')[-1])
        else:
            res.append(str(t))

    # return [v.get('value').split('/')[-1].split('#')[-1] for v in triple]
    return res


def parseGraph(g):
    ''' 
    Transform all triples in a graph to human readable strings.

    Parameters 
    ----------
    g : list
        A list containing all the triples in a graph?

    Returns
    ---
    A list of the triples (NOT GRAPH).
    '''
    parsedGraph = []
    for triple in g:
        s = triple[0].split('/')[-1]
        p = triple[1].split('/')[-1].split('#')[-1]
        o = triple[2].split('/')[-1]
        parsedGraph.append((s, p, o))
    return parsedGraph


def readGraph(fileName, mode='nt'):
    ''' Reads the knowledge base and constructs a KG of it '''
    g = rdflib.Graph()
    parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    targetFile = 'datasets/{}'.format(fileName)
    g.parse(os.path.join(parent, targetFile), format=mode)
    return g


def parsingTriple(triple):
    ''' Makes a human readable string out of a single triple of URI's'''
    s = triple[0].split('/')[-1]
    p = triple[1].split('/')[-1].split('#')[-1]
    o = triple[2].split('/')[-1]
    return (s, p, o)


def parsingGraph(g):
    ''' Transform all triples in a graph to human readable strings.
    Return: list of the triples (NOT GRAPH)'''
    parsedGraph = []
    for triple in g:
        s = triple[0].split('/')[-1]
        p = triple[1].split('/')[-1].split('#')[-1]
        o = triple[2].split('/')[-1]
        parsedGraph.append((s, p, o))
    return 


def addFilterSPARQL(yesHints = [], noHints = []):
    """
    The SPARQL query need to have the prefixes defined in order for this to work.
    Each time a question is asked, the string object is extended with the used (p,o)
    The number of total hints is equal to the number of questions asked so far.

    Parameters 
    ----------
    yesHints : list
        A list containing all the p/o combinations that the answerer responded "yes" to.
    noHints : list
        A list containing all the p/o combinations that the answerer responded "no" to.

    Returns
    ---
    A string object consisting of all yesHints and noHints to be used directly in a SPARQL query.
    """
    s = ''
    for hint in yesHints:
        (_, p, o) = hint
        s += f"\nfilter (?p != {p['prefix_entity']} || ?o != "
        if o['type'] == "literal":
            s += f"\"{o['value']}\""
            if o.get('xml:lang'): # only if there's lang we add it.
                s += f"@{o['xml:lang']}"
            s += ' )'
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


def addFilterSPARQLX(yesHints = [], noHints = []):
    """
    The SPARQL query need to have the prefixes defined in order for this to work.
    Each time a question is asked, the string object is extended with the used (p,o)
    The number of total hints is equal to the number of questions asked so far.

    Parameters 
    ----------
    yesHints : list
        A list containing all the p/o combinations that the answerer responded "yes" to.
    noHints : list
        A list containing all the p/o combinations that the answerer responded "no" to.

    Returns
    ---
    A string object consisting of all yesHints and noHints to be used directly in a SPARQL query.
    """
    s = ''
    for hint in yesHints:
        (_, p, o) = hint
        s += f"\nfilter (?p != <{p['uri']}> || ?o != "
        # if o['type'] == "literal":
        #     s += f"\"{o['value']}\""
        #     if o.get('xml:lang'): # only if there's lang we add it.
        #         s += f"@{o['xml:lang']}"
        #     s += ' )'
        # else:
        s += f"<{o['uri']}>)"

    for hint in noHints:
        (_, p, o) = hint
        s += f"\nfilter not exists {{ ?s <{p['uri']}> "
        # if o['type'] == "literal":
        #     s += f"\"{o['value']}\""
        #     if o.get('xml:lang'):
        #         s += f"@{o['xml:lang']}"
        #     s += '. }'
        # else:
        s += f"<{o['uri']}> . }}"
    return s


def load_bot(name):
    """
    Takes the name of the bot and creates an object to intialize the bot
    

    Parameters 
    ----------
    name : str
       The folder name of the bot.

    Returns
    ---
    The module of the selected bot.
    """
    path = f'bots.{name}.bot'
    module = importlib.import_module(path)
    bot = getattr(module, f'{name}Bot')
    return bot

def rescursiveQueryX(state, corruptedKG, split=0.5, depth=0, lastKnownAnswer = 'yes'):
    ''' 
    Used by the entropy bot, makes a query which retrieves the po's and thier counts.
        
    Parameters 
    ----------
    state : ??

    split : float
        Determines for the entropy bot how much it want a po combination to be able to split by. 
        if 1 chooses the po that occurs the most in the data (greedy approach).
        if 0.5 chooses the po that allows for 50% split in the data i.e. the entropy minimizing po.
        if 0.1 chooses the po that allows for 10% split in the data (minimalistic approach).

    depth : int
        Used to calculate complex entropy i.e. combination of po's.

    lastKnownAnswer : str 
        The last answer given by the answerer (default='yes'). 

    Returns
    ---
    The po combination that splits closest to the split variable.
    '''
    api = state.api
    # corruptedKG = state.corruptedKG
    if lastKnownAnswer == 'no':
        state.history = [ x for x in state.history if x != state.noHints[-1]] # takes approximately 1 millisecond
        totalCount = getCurrentCountX(state,corruptedKG) # TODO
        best = min(state.history, key=lambda x: abs(int(x[0]['value']) - int(totalCount) * split))
        return best
    # prefixes = '\n'.join(api.prefixes)
    query = f"""
    SELECT distinct ?p ?o 
            (count(?s) as ?poCount)
    WHERE {{
    ?s ?p ?o ;
        {';'.join([" <{}> <{}>".format(p['uri'], o['uri']) for (_, p, o) in state.yesHints])} .
        {addFilterSPARQLX(yesHints=state.yesHints, noHints=state.noHints)}    
    }}
    GROUP BY ?p ?o
    ORDER BY DESC (?poCount)
    """
    if not state.yesHints:
        query = f"""
        SELECT distinct ?p ?o (count(?s) as ?poCount)
        WHERE {{?s ?p ?o .
        {addFilterSPARQLX(noHints=state.noHints)} }}
        GROUP BY ?p ?o
        # having(?poCount > 1) 
        ORDER BY DESC (?poCount)
        """
    # qres = api.queryKG(query=query)
    # print("type CKG", type(corruptedKG))
    qres = corruptedKG.query(query)

    # if not qres and not state.yesHints:
    #     query = f"""
    #     {prefixes}
    #     SELECT distinct ?p ?o (count(?s) as ?poCount)
    #     WHERE {{?s ?p ?o .
    #     {addFilterSPARQL(noHints=state.noHints)} }}
    #     GROUP BY ?p ?o
    #     ORDER BY DESC (?poCount)
    #     """
    # if not qres:
    #     print('this is empty')
    # else:
    #     print('we are getting results back')

    qres = api.parseJSONX(qres, [['poCount', 'p', 'o']])

    state.history = qres 
    totalCount = getCurrentCountX(state, corruptedKG)
    if not qres:
        return []
    a = np.array([int(x[0]['value']) for x in state.history])
    if np.all(a == 1): # This means that the bot found one specific subject, and there is only one label!
        labels = list(filter(lambda x: x[1]['value'] == 'label', qres))
        # print('only labels', )
        if labels: return random.choice(labels)
    best = min(qres, key=lambda x: abs(int(x[0]['value']) - int(totalCount) * split))
    # if depth > 0:
    #     return  rescursiveQuery(state.yesHints, depth-1) #result[0]['value'], result[1]['value'], depth-1)
    # print('iets',best)
    return best

def rescursiveQuery(state, split=0.5, depth=0, lastKnownAnswer = 'yes'):
    ''' 
    Used by the entropy bot, makes a query which retrieves the po's and thier counts.
        
    Parameters 
    ----------
    state : ??

    split : float
        Determines for the entropy bot how much it want a po combination to be able to split by. 
        if 1 chooses the po that occurs the most in the data (greedy approach).
        if 0.5 chooses the po that allows for 50% split in the data i.e. the entropy minimizing po.
        if 0.1 chooses the po that allows for 10% split in the data (minimalistic approach).

    depth : int
        Used to calculate complex entropy i.e. combination of po's.

    lastKnownAnswer : str 
        The last answer given by the answerer (default='yes'). 

    Returns
    ---
    The po combination that splits closest to the split variable.
    '''
    api = state.api
    if lastKnownAnswer == 'no':
        state.history = [ x for x in state.history if x != state.noHints[-1]] # takes approximately 1 millisecond
        totalCount = getCurrentCount(state)
        best = min(state.history, key=lambda x: abs(int(x[0]['value']) - int(totalCount) * split))
        return best
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
        having(?poCount > 1) 
        ORDER BY DESC (?poCount)
        """
    qres = api.queryKG(query=query)
    if not qres and not state.yesHints:
        query = f"""
        {prefixes}
        SELECT distinct ?p ?o (count(?s) as ?poCount)
        WHERE {{?s ?p ?o .
        {addFilterSPARQL(noHints=state.noHints)} }}
        GROUP BY ?p ?o
        ORDER BY DESC (?poCount)
        """
    qres = api.parseJSON(qres, [['poCount', 'p', 'o']])
    state.history = qres 
    totalCount = getCurrentCount(state)
    if not qres:
        return []
    a = np.array([int(x[0]['value']) for x in state.history])
    if np.all(a == 1): # This means that the bot found one specific subject, and there is only one label!
        labels = list(filter(lambda x: x[1]['value'] == 'label', qres))
        # print('only labels', )
        if labels: return random.choice(labels)
    best = min(qres, key=lambda x: abs(int(x[0]['value']) - int(totalCount) * split))
    # if depth > 0:
    #     return  rescursiveQuery(state.yesHints, depth-1) #result[0]['value'], result[1]['value'], depth-1)
    # print('iets',best)
    return best

def getCurrentCount(state):
    ''' 
    Used by entropyBot, retrieves the count of po's given certain state

    Parameters 
    ----------
    state : ??

    Returns
    ---
    Po combination together with how often they occur. 
    '''
    api = state.api
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

def getCurrentCountX(state, corruptedKG):
    ''' 
    Used by entropyBot, retrieves the count of po's given certain state

    Parameters 
    ----------
    state : ??

    Returns
    ---
    Po combination together with how often they occur. 
    '''
    api = state.api
    # corruptedKG = state.corruptedKG
    # prefixes = '\n'.join(api.prefixes)
    query = f"""

    SELECT (count(?s) as ?TotalCount)
    WHERE {{
    ?s {';'.join([" <{}> <{}>".format(p['prefix_entity'], o['prefix_entity']) for (_, p, o) in state.yesHints])} .
    }}
    """
    
    if not state.yesHints:
        query = f"""
        SELECT (count(?s) as ?TotalCount)
        WHERE {{?s ?p ?o .}}
        """
    qres = corruptedKG.query(query)
    qres = api.parseJSONX(qres, [['TotalCount']])
    return qres[0][0]['value']

def readPickleBack(filename):
    ''' 
    Used to read the pickle file that stores all informations about the runs
    
    Parameters 
    ----------
    filename : str
        The name of a file.

    Returns
    ---
    A list of what is in the file. 
    '''
    a_file = open(filename, "rb")
    objs = []
    while 1:
        try:
            objs.append(pickle.load(a_file))
        except EOFError:
            break
    return objs

def retrieveName(predicate, question, state):
    """
    TODO: Documentation
    """
    api = state.api
    object = question[2]
    if predicate == 'givenName':
        query = F""" select ?name  where {{ 
        ?s <http://schema.org/givenName> <{object['uri']}>;
            <http://www.w3.org/2000/01/rdf-schema#label> ?name.
        }}"""
    elif predicate == 'sameAs':
        query = F""" select ?name  where {{ 
        ?s <http://www.w3.org/2002/07/owl#sameAs> <{object['uri']}>;
            <http://www.w3.org/2000/01/rdf-schema#label> ?name.
        }}"""
    elif predicate == 'image':
        query = F""" select ?name  where {{ 
        ?s <http://schema.org/image> <{object['uri']}>;
            <http://www.w3.org/2000/01/rdf-schema#label> ?name.
        }}"""
    qres = api.queryKG(query)
    qres = api.parseJSON(qres, [['name']])
    return qres[0][0].get('value')
    
# a = readPickleBack('tournament_output.pkl')
# print(a)