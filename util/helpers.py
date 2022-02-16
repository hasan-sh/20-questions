
import rdflib


def readGraph(file, mode='ttl'):
    g = rdflib.Graph()
    g.parse(file, format=mode)
    return g

def parseGraph(g):
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


