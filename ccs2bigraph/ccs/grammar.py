"""CCS Grammar Definition

This file contains the CCS grammar used by CAAL (https://caal.cs.aau.dk). It is expressed in pyparsing.

Atomic elements are actions, which form processes.

Processes are formed by 
- composition of alternatives A,
- parallel composition of processes P | P,
- or hiding of actions of another process (P \\ { actions... }

Alternatives are either
- empty (0), 
- prefixed processes (action.Process)
- alternative of processes (Process + Process)

Actions are
- normal (action)
- dual ('action)

TODO: Where to place renaming?
"""

import logging
logger = logging.getLogger(__name__)

import pyparsing as pp

# Comments
_comment = pp.Literal("*") + pp.restOfLine

# atomic elements: Actions
_raw_action = pp.Word(pp.alphas.lower(), pp.alphanums)
_dual_action = pp.Literal("'") + _raw_action
_action = _raw_action | _dual_action

# sets of actions:
_l_actionset_parenthesis, _r_actionset_parenthesis = pp.Literal('{'), pp.Literal('}')
_actionset_separator = pp.Literal(',')
_actionset = _l_actionset_parenthesis + pp.ZeroOrMore(_action + _actionset_separator) + _action + _r_actionset_parenthesis
_actionset_name = pp.Word(pp.alphas.upper(), pp.alphanums)

_actionset_assignment_keyword = pp.Literal("set")
_actionset_assignment_operator = pp.Literal("=")
_actionset_assignment_finalizer = pp.Literal(";")
_actionset_assignment = _actionset_assignment_keyword + _actionset_name + _actionset_assignment_operator + _actionset + _actionset_assignment_finalizer

# alternatives
# we do need a notion of processes already, however they aren't (fully) defined yet.
_process = pp.Forward()
_process_name = pp.Word(pp.alphas.upper(), pp.alphanums)

# we also do need prefix operation as one alternative
_prefix_operator = pp.Literal('.')
_prefix = _action + _prefix_operator + _process

_empty_alternative = pp.Literal('0')
_alternative_operator = pp.Literal('+')

# alternatives are recursively defined (similar to processes)
_alternative = pp.Forward()
_alternative <<= _empty_alternative | _prefix | _alternative + _alternative_operator + _alternative

# actual process definition
# hiding
_hiding_operator = pp.Literal('\\')
_hiding = _process + _hiding_operator + (_actionset | _actionset_name)

# parallel composition
_parallel_operator = pp.Literal('|')
_parallel = _process + _parallel_operator + _process

# renaming (here?)
# _l_renaming_operator, _r_renaming_operator = pp.Literal('['), pp.Literal(']')
# _renaming = _l_renaming_operator + _process + _r_renaming_operator

_process <<= _alternative | _hiding | _parallel

_process_assignment_operator = pp.Literal('=')
_process_assignment_finalizer = pp.Literal(';')
_process_assignment = _process_name + _process_assignment_operator + _process + _process_assignment_finalizer

_ccs_input = pp.ZeroOrMore(_process_assignment | _actionset_assignment)
_ccs_input.ignore(_comment)

def parse(raw: str):
    logger.info(f"Trying to parse {raw}")
    res = _ccs_input.parse_string(raw)
    logger.info(f"Done parsing {raw}")
    return res


