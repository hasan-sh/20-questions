import os
import rdflib
from pathlib import Path
import random
from util import constants

def readGraph(fileName, mode='nt'):
    ''' Reads the knowledge base and constructs a KG of it '''
    g = rdflib.Graph()
    parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    targetFile = 'datasets/{}'.format(fileName)
    g.parse(os.path.join(parent, targetFile), format=mode)
    return g

def parseTriple(triple):
    ''' Makes a human readable string out of a single triple of URI's'''
    s = triple[0].split('/')[-1]
    p = triple[1].split('/')[-1].split('#')[-1]
    o = triple[2].split('/')[-1]
    return (s, p, o)

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
    if yesHints:
        for hint in yesHints: 
            # print(hint)
            (_, p, o) = hint
            if p in constants.literalPredicates:
                ## TODO: Make a list of all literal predicates that refer to a literal in the graph.
                # We found three so far but it needs to be automated (sparql query)
                s += 'filter (?p != <' + p + '> || ?o != "' + o + '") \n'
            else:
                s += 'filter (?p != <' + p + '> || ?o != <' + o + '>) \n'
    if noHints:
        s += 'filter not exists {'
        for hint in noHints: 
        # print(hint)
            (_, p, o) = hint
            if p in constants.literalPredicates:
                ## TODO: Make a list of all literal predicates that refer to a literal in the graph.
                # We found three so far but it needs to be automated (sparql query)
                s += '?s <' + p + '> "' + o + '". \n'
            else:
                s += '?s <' + p + '> <' + o + '>. \n'
        s += '}'
    return s
