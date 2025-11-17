"""CCS to Bigraph Transformation

This tool allows to transform CCS process definitions
"""

import argparse
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

import ccs2bigraph.config as config
import ccs2bigraph.ccs.grammar as ccs_grammar
from ccs2bigraph.translation import FiniteCcsTranslator

def main():
    logging.basicConfig(filename='ccs2bigraph.log', level=logging.INFO)
    logger.info("CSS2Bigraph - Welcome")

    # Define command line arguments
    parser = argparse.ArgumentParser(
        prog='ccs2bigraph',
        description='Translation of CCS Expressions to bigraph counterparts'
    )

    parser.add_argument("inputfile", help="CSS file for translation", type=Path)
    parser.add_argument("initial", help="Process used as initial state in the resulting bigraphical reactive system")
    parser.add_argument("-a", "--add-actions", help="Merges all occuring actions to Nil when occuring the 0 process", action="store_true")

    # Parse command line arguments
    args = parser.parse_args()

    # Evaluate command line arguments
    logger.info(f"Using {args.inputfile} as input file")
    input_file_name = Path(args.inputfile)

    logger.info(f"Using {args.initial} as init process")
    init_process = args.initial

    logger.info(f"Set add_actions to {args.add_actions}")
    config.add_actions = args.add_actions

    logger.info("Opening input file")
    with open(input_file_name) as input_file:
        logger.info("Reading input file")
        ccs_input = input_file.read()

        logger.info("Parsing input file to CCS representation")
        ccs = ccs_grammar.parse(ccs_input)

        logger.info("Translating to Bigraph representation")
        translator = FiniteCcsTranslator(ccs, init_process)
        
        bigraph = translator.translate()

        logger.info("Printing Bigraph to stdout")
        print(bigraph)

    logger.info("Done. Goodbye.")

if __name__ == "__main__":
    main()