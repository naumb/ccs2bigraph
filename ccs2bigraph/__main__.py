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
    parser.add_argument("control-template", help="Template for the controls in the resulting bigrapher input file", type=Path)
    parser.add_argument("bigraphs-template", help="Template for the (general) bigraphs in the resulting bigrapher input file", type=Path)
    parser.add_argument("reactions-template", help="Template for the reactions in the resulting bigrapher input file", type=Path)
    parser.add_argument("brs-template", help="Template for the brs definions in the resulting bigrapher input file", type=Path)

    # Parse command line arguments
    args = parser.parse_args()

    # Evaluate command line arguments
    logger.info(f"Using {args.inputfile} as ccs input file")
    input_file_name = Path(args.inputfile)

    logger.info(f"Using {args.initial} as init process")
    init_process = args.initial

    logger.info(f"Using {args.control_template} as template for the control definitions")
    config.control_template = args.control_template

    logger.info(f"Using {args.bigraphs_template} as template for the (general) bigraph definitions")
    config.bigraphs_template = args.bigraphs_template

    logger.info(f"Using {args.reactions_template} as template for the reaction definitions")
    config.reactions_template = args.reactions_template

    logger.info(f"Using {args.brs_template} as template for the brs definitions")
    config.brs_template = args.brs_template

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