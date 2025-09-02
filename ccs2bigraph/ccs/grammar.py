"""
CCS Grammar Definition

This file contains the CCS grammar used by CAAL (https://caal.cs.aau.dk). It is expressed in pyparsing.

Atomic elements are actions, which form processes.

Processes are defined by
- 0, the empty process, also called nil
- named processes, e.g. "A"

Processes can be formed by
- renaming, e.g. "A[b/a]" or "(a.0)[c/b, e/d]" (note the precedence of .)
- hiding, e.g. "A \\ {a, b}" or (a.b.c.0) \\ {a} or (a.b.c.d.0) \\ H where H is a name of a set
- prefixing by actions, e.g. "a.0"
- alternative composition, e.g. "a.0 + B + 0"
- parallel composition, e.g. "a.0 | B | 0"

We implement these rules as an infix grammar, where processes 
"""

import logging
logger = logging.getLogger(__name__)

import pyparsing as pp

from .representation import Action, ActionSet, AlternativeProcesses, HidingProcess, NamedActionSet, NamedProcess, NilProcess, ParallelProcesses, PrefixedProcess, ProcessAssignment, RenamingProcess

# Comments
_comment = pp.Literal("*") + pp.restOfLine

# atomic elements: Actions
_raw_action = pp.Word(pp.alphas.lower(), pp.alphanums)
_dual_action = pp.Suppress("'") + _raw_action

_raw_action.setParseAction(lambda t: Action(t[0], False))
_dual_action.setParseAction(lambda t: t[0].get_dual_action())

_action = _raw_action | _dual_action

# sets of actions:
_l_actionset_parenthesis, _r_actionset_parenthesis = map(pp.Suppress, ['{', '}'])
_actionset_separator = pp.Suppress(',')
_actionset = _l_actionset_parenthesis + pp.ZeroOrMore(_raw_action + _actionset_separator) + _action + _r_actionset_parenthesis
_actionset.setParseAction(lambda t: ActionSet(t.as_list()))

_actionset_name = pp.Word(pp.alphas.upper(), pp.alphanums)

_actionset_assignment_keyword = pp.Suppress("set")
_actionset_assignment_operator = pp.Suppress("=")
_actionset_assignment_finalizer = pp.Suppress(";")
_actionset_assignment = _actionset_assignment_keyword + _actionset_name + _actionset_assignment_operator + _actionset + _actionset_assignment_finalizer
_actionset_assignment.setParseAction(lambda t: NamedActionSet(t[0], t[1]))

# processes
# we do need a notion of processes already, however they aren't (fully) defined yet.
_process_name = pp.Word(pp.alphas.upper(), pp.alphanums)
_process_name.setParseAction(lambda t: NamedProcess(t[0]))

# empty process as starting point
_nil_process = pp.Suppress('0')
_nil_process.setParseAction(NilProcess)

_process_atom = _process_name | _nil_process

# define the infix grammar rules
_prefix_operator = pp.Suppress('.')
_parallel_operator = pp.Suppress('|')
_alternative_operator = pp.Suppress('+')

_hiding_operator = pp.Suppress('\\')
_hiding_rule = _hiding_operator + (_actionset | _actionset_name)

_l_renaming_operator, _r_renaming_operator = map(pp.Suppress, ['[', ']'])
_inner_renaming_operator = pp.Suppress("/")
_inner_renaming = pp.Group(_action + _inner_renaming_operator + _action)
_inner_renaming_seperator = pp.Suppress(",")
_renaming_rule = _l_renaming_operator + pp.ZeroOrMore(_inner_renaming + _inner_renaming_seperator) + _inner_renaming + _r_renaming_operator

_process = pp.infix_notation(
    _process_atom,
    [
        (_renaming_rule, 1, pp.opAssoc.LEFT, lambda t: RenamingProcess(t[0][0], list((tt[0], tt[1]) for tt in t[0][1:]))),
        (_hiding_rule, 1, pp.opAssoc.LEFT, lambda t: HidingProcess(t[0][0], t[0][1])),
        (_action + _prefix_operator, 1, pp.opAssoc.RIGHT, lambda t: PrefixedProcess(t[0][0], t[0][1])),
        (_parallel_operator, 2, pp.opAssoc.LEFT, lambda t: ParallelProcesses(t[0].asList())),
        (_alternative_operator, 2, pp.opAssoc.LEFT, lambda t: AlternativeProcesses(t[0].asList()))
    ]
)

_process_assignment_operator = pp.Suppress('=')
_process_assignment_finalizer = pp.Suppress(';')
_process_assignment = _process_name + _process_assignment_operator + _process + _process_assignment_finalizer

_process_assignment.addParseAction(lambda t: ProcessAssignment(t[0], t[1]))

_ccs_input = pp.ZeroOrMore(_process_assignment | _actionset_assignment)
_ccs_input.ignore(_comment)

def parse(raw: str):
    logger.info(f"Trying to parse {raw}")
    res = _ccs_input.parse_string(raw)[0]
    logger.info(f"Done parsing {raw}")
    return res


