"""
Representation of CCS Terms (c.f. CAAL Syntax)

This file provides classes for the individual parts of CCS terms, i.e.
- actions
- processes, especially in form of
  - 0
  - prefixed processes
  - alternative processes
  - parallel processes
  - renamed processes
  - hiding processes
"""

import logging
logger = logging.getLogger(__name__)

from abc import ABC
from dataclasses import dataclass

@dataclass(frozen=True)
class Action(object):
    """
    Represents Actions of CCS Terms
    
    :param str name: The name of the Action, starting with a lowercase character

    Example
    >>> str(Action('a'))
    'a'
    """

    name: str

    def __str__(self) -> str:
        return f"{self.name}"
    
@dataclass(frozen=True)
class DualAction(Action):
    """
    Represents Dual Actions of CCS Terms
    
    :param str name: The name of the Action, starting with a lowercase character
    :param bool is_dual: Whether or not the action is in it's dual form (e.g. 'a)

    :const 

    Example
    >>> str(DualAction('x'))
    "'x"
    """

    def __str__(self) -> str:
        return f"'{self.name}"

@dataclass(frozen=True)
class ActionSet(object):
    """
    Represents a set of `Action`s, used for instance in `HidingProcess`.

    :param list[Action] actions: The set of actions in the `ActionSet`
    
    Example:
    >>> str(ActionSet([Action("a")]))
    '{a}'
    """
    actions: list[Action]

    def __str__(self) -> str:
        return "{" + ", ".join(map(str, self.actions)) + "}"
    
@dataclass(frozen=True)
class ActionSetByName(object):
    """
    Refers to an `ActionSetAssignment` by its name.

    :param str name: Name of the referenced `ActionSetAssignment`
    
    Example:
    >>> str(ActionSetByName("A"))
    'A'
    """
    name: str

    def __str__(self) -> str:
        return self.name

@dataclass(frozen=True)
class ActionSetAssignment(object):
    """
    Assignment of an `ActionSet` to a name.

    :param str name: The name to which the `ActionSet` is assigned
    :param ActionSet actionSet: The assigned `ActionSet` itself

    Example:
    >>> str(ActionSetAssignment("H", ActionSet(list(map(Action, ["a", "b", "c"])))))
    'set H = {a, b, c};'
    """
    name: str
    actionSet: ActionSet

    def __str__(self) -> str:
        return f"set {self.name} = {self.actionSet};"

class Process(ABC):
    """
    Abstract Base Class for CCS process definitions
    """
    pass

@dataclass(frozen=True)
class NilProcess(Process):
    """
    The empty process.

    Example:
    >>> str(NilProcess())
    '0'
    """

    def __str__(self):
        return "0"
    
@dataclass(frozen=True)
class ProcessByName(Process):
    """
    Refers to an `ProcessAssignment` by its name.

    :param str name: Name of the referenced `ProcessAssignment`
    
    Example:
    >>> str(ProcessByName("A"))
    'A'
    """
    name: str
    
    def __str__(self):
        return self.name

@dataclass(frozen=True)
class PrefixedProcess(Process):
    """
    Process representing the result of a prefix operation.

    :param Action prefix: The `Action` by which `remaining` is prefixed
    :param Process remaining: The remaining process after the `prefix` action

    Example:
    >>> str(PrefixedProcess(Action('a'), NilProcess()))
    '(a.0)'
    >>> str(PrefixedProcess(Action('a'), PrefixedProcess(DualAction('b'), NilProcess())))
    "(a.('b.0))"
    """
    prefix: Action
    remaining: Process
    
    def __str__(self) -> str:
        return f"({self.prefix}.{self.remaining})"

@dataclass(frozen=True)
class HidingProcess(Process):
    """
    Process representing the result of a hiding operation

    :param Process process: The `Process` of which actions will be hidden
    :param ActionSet | ActionSetByName hiding: An `ActionSet` or a corresponding name of an `ActionSetAssignment` that defines the hidden `Actions`.

    Example:
    >>> str(HidingProcess(PrefixedProcess(Action('a'), NilProcess()), ActionSet(list(map(Action, ["a", "b"])))))
    '((a.0) \\\\ {a, b})'
    >>> str(HidingProcess(PrefixedProcess(Action('a'), NilProcess()), ActionSetByName("H")))
    '((a.0) \\\\ H)'
    """
    process: Process
    hiding: ActionSet | ActionSetByName
    
    def __str__(self) -> str:
        return f"({self.process} \\ {self.hiding})"

@dataclass(frozen=True)
class RenamingProcess(Process):
    """
    Process representing the result of a renaming operation

    :param Process process: The `Process` of which actions will be renamed
    :param list[tuple[Action, Action]] renaming: A list of renaming operations, i.e. tuples of `(Action(new_name), Action(old_name))`

    Example:
    >>> str(RenamingProcess(PrefixedProcess(Action('a'), NilProcess()), [(Action("b"), Action("a")), (Action("y"), Action("z"))]))
    '((a.0)[b/a, y/z])'
    """
    process: Process
    renaming: list[tuple[Action, Action]]

    def __str__(self) -> str:
        return f"({self.process}[" + ", ".join(f"{new}/{old}" for (new, old) in self.renaming) + "])"

@dataclass(frozen=True)
class AlternativeProcesses(Process):
    """
    Process representing the result of one (or more consequtive) alternative operations

    :param list[Process] alternatives: The alternative processes

    Example:
    >>> str(AlternativeProcesses([PrefixedProcess(Action('a'), NilProcess()), PrefixedProcess(Action('b'), NilProcess()), PrefixedProcess(Action('c'), NilProcess())]))
    '((a.0) + (b.0) + (c.0))'
    """
    alternatives: list[Process]
    
    def __str__(self) -> str:
        return "(" + " + ".join(map(str, self.alternatives)) + ")"

@dataclass(frozen=True)
class ParallelProcesses(Process):
    """
    Process representing the result of one (or more consequtive) parallel composition operations

    :param list[Process] parallels: The parallel processes

    Example:
    >>> str(ParallelProcesses([PrefixedProcess(Action('a'), NilProcess()), PrefixedProcess(Action('b'), NilProcess()), PrefixedProcess(Action('c'), NilProcess())]))
    '((a.0) | (b.0) | (c.0))'
    """
    parallels: list[Process]
    
    def __str__(self) -> str:
        return "(" + " | ".join(map(str, self.parallels)) + ")"
    
@dataclass(frozen=True)
class ProcessAssignment:
    """
    Assignment of a `Process` to a name.

    :param str name: The name to which the `Process` is assigned
    :param Process process: The assigned `Process` itself

    Example:
    >>> str(ProcessAssignment("A", NilProcess()))
    'A = 0;'
    >>> str(RenamingProcess(PrefixedProcess(Action('a'), NilProcess()), [(Action("b"), Action("a")), (Action("y"), Action("z"))]))
    '((a.0)[b/a, y/z])'
    """
    name: str
    process: Process

    def __str__(self) -> str:
        return f"{self.name} = {self.process};"
    
@dataclass(frozen=True)
class Ccs:
    """
    Representation a closed CCS expression.

    :param list[ProcessAssignment] processes: The defined processes in the CCS expression
    :param list[ActionSetAssignment] action_sets: The defined action sets in the CCS expression
    """
    processes: list[ProcessAssignment]
    action_sets: list[ActionSetAssignment]