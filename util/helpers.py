import os
import rdflib
from pathlib import Path
import random

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

# def to_simple_triples(file, destination_file, mode):
#     # reading the nt file
#     print(end='Loading data... ', flush=True)

#     g = rdflib.Graph()
#     g.parse(file, format=mode)

#     print('OK ')

#     # opening the destination file in append mode
#     file_object = open(destination_file, 'a', encoding="utf-8")

#     for triple in g:
#         s, p, o = parse_uri(triple)
#         # Append spo (tab separated at the end of file)
#         file_object.write(s+'\t'+p+'\t'+o)
#         file_object.write('\n')
#     file_object.close()
#     print('Done')


