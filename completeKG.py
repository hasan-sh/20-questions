
from argparse import ArgumentParser

from CompleteKG import main
from validateTriples import getWikidataId, validate

parser = ArgumentParser()

parser.add_argument("-f", "--file-name",
                    dest="fileName",
                    help="File name to read from (Default: tournament_runs.pkl)",
                    type=str,
                    default="tournament_runs.pkl")

parser.add_argument("-t", "--test",
                    dest="test",
                    help="Run the test&examples",
                    type=bool,
                    default=False)

parser.add_argument("-d", "--development",
                    dest="dev",
                    help="Development mode (default: False)",
                    default=True)

parser.add_argument("-n", "--no-hints",
                    dest="noHints",
                    help="Not or yes hints (False: yes hints, True: no hints.)",
                    type=bool,
                    default=True)

options = parser.parse_args()
fileName = options.fileName
test = options.test
dev = options.dev == True
noHints = options.noHints
if __name__ == '__main__':
    completeKG = main.CompleteKG(fileName, noHints, dev)
    if test:
        completeKG.runExamples()
    else:
        triples = completeKG.run()
        toValidate = set()
        for triple in triples:
            toValidate.add((triple['entity'], getWikidataId(triple['entity'])))
        validate(toValidate)
        
        print('Next step is to validate the chosen triples by checking their existence on wikidata!!')