"""
Finite Pure CCS Grammar Definition

This file contains the CCS Grammar defined by Milner in "Pure bigraphs: Structure and dynamics"

In EBNF, it looks like this:

P ::= 0 | /x P | P|P | M  - Process definitions (note that P|P is parallel composition)
M ::= l.P | M+M           - Alternative definitions
l ::= 'x | x              - Action definitions  



Note, that all prefix operations go through an alternative derivation
Note, that hiding is written as /xP instead of νxP or vxP
Note, that there are no recursive definitions, and renaming is abscent
Note, that expressions like "0 + 0" or even "P + 0" for any P are not valid in this grammar, since all alternatives need to be prefixed.

We implement this as a multi-layer infix grammar
"""

import logging
logger = logging.getLogger(__name__)

import pyparsing as pp
import typing as tp

from .representation import Action, ActionSet, SumProcesses, DualAction, HidingProcess, NilProcess, ParallelProcesses, PrefixedProcess, Process

# Performance
pp.ParserElement.enable_packrat()

# Comments
_comment = pp.Literal("*") + pp.restOfLine

# atomic elements: Actions
_raw_action = pp.Word(pp.alphas.lower(), pp.alphanums)
_dual_action = pp.Suppress("'") + _raw_action.copy()

def _raw_action_parse_action(pr: pp.ParseResults) -> Action:
    return Action(tp.cast(str, pr[0]))

_raw_action.setParseAction(_raw_action_parse_action)

def _dual_action_parse_action(pr: pp.ParseResults) -> DualAction:
    return DualAction(tp.cast(str, pr[0]))

_dual_action.setParseAction(_dual_action_parse_action)

_action = _raw_action | _dual_action

# process defintion and operations
# 0 process
_nil_process = pp.Suppress('0')
_nil_process.setParseAction(NilProcess)

# hiding
def _hiding_parse_action(pr: pp.ParseResults) -> HidingProcess:
    return HidingProcess(
        tp.cast(Process, pr[0][1]), 
        ActionSet([tp.cast(Action, pr[0][0])])
    )

_hiding_operator = pp.Suppress('/')
_hiding = _hiding_operator + _raw_action

# parallel
_parallel_operator = pp.Suppress('|')

def _parallel_parse_action(pr: pp.ParseResults) -> ParallelProcesses:
    return ParallelProcesses(tp.cast(list[Process], pr.as_list()[0])) # pyright: ignore[reportUnknownMemberType]

# process will be defined as an infix grammar
_process = pp.Forward()

# alternative operations

# prefix
def _prefix_parse_action(pr: pp.ParseResults) -> PrefixedProcess:
    return PrefixedProcess(
        tp.cast(Action, pr[0]),  
        tp.cast(Process, pr[1])
    )
_prefix_operator = pp.Suppress('.')
_prefix = _action + _prefix_operator + _process
_prefix.setParseAction(_prefix_parse_action)

# sums
def _sum_parse_action(pr: pp.ParseResults) -> SumProcesses:
    return SumProcesses(tp.cast(list[Process], pr.as_list()[0])) # pyright: ignore[reportUnknownMemberType]
_sum_operator = pp.Suppress('+')

_alternative_atom = _prefix
_alternative = pp.infix_notation(
    _alternative_atom,
    [
        (_sum_operator, 2, pp.opAssoc.LEFT, _sum_parse_action)
    ]
)

# finish process defintion
_process_atom = _nil_process
_process <<= pp.infix_notation(
    _process_atom,
    [
        (_parallel_operator, 2, pp.opAssoc.LEFT, _parallel_parse_action),
        (_hiding, 1, pp.opAssoc.RIGHT, _hiding_parse_action),
    ]
) | _alternative

def parse(raw: str) -> Process:
    """pure finite CCS parsing"""
    logger.info(f"Trying to parse {raw}")
    res = tp.cast(Process, _process.parse_string(raw, True)[0])
    logger.info(f"Done parsing {raw}")
    return res