"""CCS to Bigraph Transformation

This tool allows to transform CCS process definitions
"""

import logging
logger = logging.getLogger(__name__)

# from .ccs import parser

def main():
    logging.basicConfig(filename='ccs2bigraph.log', level=logging.INFO)
    logger.info("CSS2Bigraph - Welcome")
    

    logger.info("Goodbye.")

if __name__ == "__main__":
    main()