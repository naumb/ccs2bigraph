"""CCS to Bigraph Transformation

This tool allows to transform CCS process definitions
"""

import sys
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

import ccs2bigraph.ccs.grammar as ccs_grammar
from ccs2bigraph.translation import FiniteCcsTranslator


def usage():
    print(f"Usage: {sys.argv[0]} input-file initial-process")
    print("input-file: CCS-File")
    print("inital-process: process whose representation will be used as the initial bigraph of the resulting bigraphical reaction system")

def main():
    logging.basicConfig(filename='ccs2bigraph.log', level=logging.INFO)
    logger.info("CSS2Bigraph - Welcome")

    if len(sys.argv) != 3:
        logger.error(f"Invalid command line arguments {sys.argv} passed. Will show usage and quit.")
        usage()
        exit(-1)

    logger.info(f"Using {sys.argv[1]} as input file")
    input_file_name = Path(sys.argv[1])

    logger.info(f"Using {sys.argv[2]} as init process")
    init_process = sys.argv[2]

    logger.info("Opening input file")
    with open(input_file_name) as input_file:
        logger.info("Reading input file")
        ccs_input = input_file.read()

        logger.info("Parsing input file to CCS representation")
        ccs = ccs_grammar.parse(ccs_input)

        logger.info("Translating to Bigraph representation")
        translator = FiniteCcsTranslator(ccs)
        
        bigraph = translator.translate(init_process)

        logger.info("Printing Bigraph to stdout")
        print(bigraph)

    logger.info("Done. Goodbye.")

if __name__ == "__main__":
    main()