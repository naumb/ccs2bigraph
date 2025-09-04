"""
CCS Grammar Definition

This file contains the CCS grammar used by CAAL (https://caal.cs.aau.dk). It is expressed in pyparsing.

Atomic elements are actions, which form processes.

Processes (Operands) are defined by
- 0, the empty process, also called nil
- named processes, e.g. "A"

Operations:
- renaming, e.g. "A[b/a]" or "(a.0)[c/b, e/d]" (note the precedence of .)
- hiding, e.g. "A \\ {a, b}" or (a.b.c.0) \\ {a} or (a.b.c.d.0) \\ H where H is a name of a set
- prefixing by actions, e.g. "a.0"
- parallel composition, e.g. "a.0 | B | 0"
- alternative composition, e.g. "a.0 + B + 0"

We implement these rules as an infix grammar.

Furthermore, Actions and Action-Sets as well as corresponding assignments are implemented.
"""

import logging
logger = logging.getLogger(__name__)

import pyparsing as pp
import typing as tp

from .representation import Action, ActionSet, ActionSetAssignment, AlternativeProcesses, Ccs, DualAction, HidingProcess, ActionSetByName, ProcessByName, NilProcess, ParallelProcesses, PrefixedProcess, ProcessAssignment, RenamingProcess, Process

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

# sets of actions:
_l_actionset_parenthesis, _r_actionset_parenthesis = map(pp.Suppress, ['{', '}'])
_actionset_separator = pp.Suppress(',')
_actionset = _l_actionset_parenthesis + pp.ZeroOrMore(_raw_action + _actionset_separator) + _raw_action + _r_actionset_parenthesis

def _actionset_parse_action(pr: pp.ParseResults) -> ActionSet:
    return ActionSet(tp.cast(list[Action], pr.as_list())) # pyright: ignore[reportUnknownMemberType]

_actionset.setParseAction(_actionset_parse_action)

_actionset_name = pp.Word(pp.alphas.upper(), pp.alphanums + "!#'-?^_")

def _actionset_name_parse_action(pr: pp.ParseResults) -> ActionSetByName:
    return ActionSetByName(tp.cast(str, pr[0]))

_actionset_name.set_parse_action(_actionset_name_parse_action)

_actionset_assignment_keyword = pp.Suppress("set")
_actionset_assignment_name = pp.Word(pp.alphas.upper(), pp.alphanums + "!#'-?^_")
_actionset_assignment_operator = pp.Suppress("=")
_actionset_assignment_finalizer = pp.Suppress(";")
_actionset_assignment = _actionset_assignment_keyword + _actionset_assignment_name + _actionset_assignment_operator + _actionset + _actionset_assignment_finalizer

def _actionset_assignment_parse_action(pr: pp.ParseResults) -> ActionSetAssignment:
    return ActionSetAssignment(tp.cast(str, pr[0]), tp.cast(ActionSet, pr[1]))

_actionset_assignment.setParseAction(_actionset_assignment_parse_action)

# processes
# we do need a notion of processes already, however they aren't (fully) defined yet.
_process_name = pp.Word(pp.alphas.upper(), pp.alphanums + "!#'-?^_")

def _process_name_parse_action(pr: pp.ParseResults) -> ProcessByName:
    return ProcessByName(tp.cast(str, pr[0]))

_process_name.setParseAction(_process_name_parse_action)

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

# define parse actions for individual operators
def _renaming_parse_action(pr: pp.ParseResults) -> RenamingProcess:
    return RenamingProcess(
        tp.cast(Process, pr[0][0]), 
        list(
            (r[0], r[1]) 
            for r 
            in tp.cast(list[tuple[Action, Action]], pr[0][1:])
        )
    )

def _hiding_parse_action(pr: pp.ParseResults) -> HidingProcess:
    return HidingProcess(
        tp.cast(Process, pr[0][0]), 
        tp.cast(ActionSet | ActionSetByName, pr[0][1])
    )

def _prefixed_parse_action(pr: pp.ParseResults) -> PrefixedProcess:
    return PrefixedProcess(
        tp.cast(Action, pr[0][0]), 
        tp.cast(Process, pr[0][1])
    )

def _parallel_parse_action(pr: pp.ParseResults) -> ParallelProcesses:
    return ParallelProcesses(tp.cast(list[Process], pr.as_list()[0])) # pyright: ignore[reportUnknownMemberType]

def _alternative_parse_action(pr: pp.ParseResults) -> AlternativeProcesses:
    return AlternativeProcesses(tp.cast(list[Process], pr.as_list()[0])) # pyright: ignore[reportUnknownMemberType]

# overall process definition including operators
_process = pp.infix_notation(
    _process_atom,
    [
        # (_renaming_rule, 1, pp.opAssoc.LEFT, lambda t: RenamingProcess(t[0][0], list((tt[0], tt[1]) for tt in t[0][1:]))),
        (_renaming_rule, 1, pp.opAssoc.LEFT, _renaming_parse_action),
        (_hiding_rule, 1, pp.opAssoc.LEFT, _hiding_parse_action),
        (_action + _prefix_operator, 1, pp.opAssoc.RIGHT, _prefixed_parse_action),
        (_parallel_operator, 2, pp.opAssoc.LEFT, _parallel_parse_action),
        (_alternative_operator, 2, pp.opAssoc.LEFT, _alternative_parse_action)
    ]
)

# process assignment
_process_assignment_name = pp.Word(pp.alphas.upper(), pp.alphanums + "!#'-?^_")
_process_assignment_operator = pp.Suppress('=')
_process_assignment_finalizer = pp.Suppress(';')
_process_assignment = _process_assignment_name + _process_assignment_operator + _process + _process_assignment_finalizer

def _process_assignment_parse_action(pr: pp.ParseResults) -> ProcessAssignment:
    return ProcessAssignment(
        tp.cast(str, pr[0]),
        tp.cast(Process, pr[1])
    )

_process_assignment.setParseAction(_process_assignment_parse_action)

# overall grammar for multiple process or action set assignments, corresponds to input files.
_ccs = pp.ZeroOrMore(_process_assignment | _actionset_assignment)
_ccs.ignore(_comment)

def _ccs_parse_action(pr: pp.ParseResults) -> Ccs:
    res = Ccs(
        list(filter(lambda r: isinstance(r, ProcessAssignment), pr)), # pyright: ignore[reportUnnecessaryIsInstance]
        list(filter(lambda r: isinstance(r, ActionSetAssignment), pr)) # pyright: ignore[reportUnnecessaryIsInstance]
    )

    return res

_ccs.set_parse_action(_ccs_parse_action)

def parse(raw: str) -> Ccs:
    """CCS Process file (c.f. CAAL input) parsing"""
    logger.info(f"Trying to parse {raw}")
    res = tp.cast(Ccs, _ccs.parse_string(raw, True)[0])
    logger.info(f"Done parsing {raw}")
    return res
