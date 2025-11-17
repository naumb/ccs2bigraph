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
from typing import Self

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

    Example
    >>> str(DualAction('x'))
    "'x"
    """

    def __str__(self) -> str:
        return f"'{self.name}"

@dataclass(frozen=True)
class Renaming(object):
    """
    Represents a single renaming of a CCS action

    :param Action new: The new action name
    :param Action old: The old action name which will be renamed
    """

    new: Action
    old: Action

    def __str__(self) -> str:
        return f"{self.new}/{self.old}"

@dataclass()
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
    
@dataclass()
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

@dataclass()
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

    :param Self | None parent: The parent process of each parent expression. For example, the :class:`NilProcess` in `a.0` has the `PrefixedProcess(Action("a"), NilProcess)` as its parent.  
    """

    def __init__(self, *, parent: Self | None = None):
        self.parent = parent

@dataclass()
class NilProcess(Process):
    """
    The empty process.

    Example:
    >>> str(NilProcess())
    '0'
    """

    def __post_init__(self):
        super().__init__()

    def __str__(self):
        return "0"
    
@dataclass()
class ProcessByName(Process):
    """
    Refers to an `ProcessAssignment` by its name.

    :param str name: Name of the referenced `ProcessAssignment`
    
    Example:
    >>> str(ProcessByName("A"))
    'A'
    """
    name: str

    def __post_init__(self):
        super().__init__()
    
    def __str__(self):
        return self.name

@dataclass()
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

    def __post_init__(self):
        super().__init__()
    
    def __str__(self) -> str:
        return f"({self.prefix}.{self.remaining})"

@dataclass()
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

    def __post_init__(self):
        super().__init__()
    
    def __str__(self) -> str:
        return f"({self.process} \\ {self.hiding})"

@dataclass()
class RenamingProcess(Process):
    """
    Process representing the result of a renaming operation

    :param Process process: The :class:`Process` of which actions will be renamed
    :param list[Renaming] renaming: A list of renaming operations

    Example:
    >>> str(RenamingProcess(
    ...    PrefixedProcess(Action('a'), NilProcess()),
    ...    [
    ...        Renaming(Action("b"), Action("a")), 
    ...        Renaming(Action("y"), Action("z"))
    ...    ]
    ... ))
    '((a.0)[b/a, y/z])'
    """
    process: Process
    renaming: list[Renaming]

    def __post_init__(self):
        super().__init__()

    def __str__(self) -> str:
        return f"({self.process}[" + ", ".join(map(str, self.renaming)) + "])"

@dataclass()
class SumProcesses(Process):
    """
    Process representing the result of one (or more consequtive) alternative operations

    :param list[Process] sums: The alternative processes

    Example:
    >>> str(SumProcesses([PrefixedProcess(Action('a'), NilProcess()), PrefixedProcess(Action('b'), NilProcess()), PrefixedProcess(Action('c'), NilProcess())]))
    '((a.0) + (b.0) + (c.0))'
    """
    sums: list[Process]

    def __post_init__(self):
        super().__init__()
    
    def __str__(self) -> str:
        return "(" + " + ".join(map(str, self.sums)) + ")"

@dataclass()
class ParallelProcesses(Process):
    """
    Process representing the result of one (or more consequtive) parallel composition operations

    :param list[Process] parallels: The parallel processes

    Example:
    >>> str(ParallelProcesses([PrefixedProcess(Action('a'), NilProcess()), PrefixedProcess(Action('b'), NilProcess()), PrefixedProcess(Action('c'), NilProcess())]))
    '((a.0) | (b.0) | (c.0))'
    """
    parallels: list[Process]

    def __post_init__(self):
        super().__init__()
    
    def __str__(self) -> str:
        return "(" + " | ".join(map(str, self.parallels)) + ")"
    
@dataclass()
class ProcessAssignment:
    """
    Assignment of a `Process` to a name.

    :param str name: The name to which the `Process` is assigned
    :param Process process: The assigned `Process` itself

    Example:
    >>> str(ProcessAssignment("A", NilProcess()))
    'A = 0;'
    """
    name: str
    process: Process

    def __str__(self) -> str:
        return f"{self.name} = {self.process};"
    
@dataclass()
class CcsRepresentation:
    """
    Representation a closed CCS expression.

    :param list[ProcessAssignment] process_assignments: The defined processes in the CCS expression
    :param list[ActionSetAssignment] action_set_assignments: The defined action sets in the CCS expression
    """
    process_assignments: list[ProcessAssignment]
    action_set_assignments: list[ActionSetAssignment]

    def get_all_actions(self) -> set[Action]:
        """
        Collects all actions present in the given CCS Representation. This includes all actions used in the processes in their non-dual form as well as all actions present in any defined action set
        """
        actions: set[Action] = set()
        
        # Gather actions from action set assignments
        for asa in self.action_set_assignments:
            actions = actions.union(set(asa.actionSet.actions))

        # Gather actions from process assignments
        def _gather_helper(p: Process) -> set[Action]:
            match p:
                case NilProcess() | ProcessByName(): return set()
                case PrefixedProcess(prefix=prefix, remaining=remaining):
                    # Construct new (non-dual) action with the same name
                    return _gather_helper(remaining).union(set([Action(prefix.name)]))
                case HidingProcess(process=process, hiding=hiding):
                    if isinstance(hiding, ActionSet): return _gather_helper(process).union(set(hiding.actions))
                    else: return _gather_helper(process)
                case RenamingProcess(process=process, renaming=renaming):
                    return _gather_helper(process).union(
                        # Again, construct new (non-dual) actions with the same name
                        set([Action(r.new.name) for r in renaming])
                    )
                case SumProcesses(sums=processes) | ParallelProcesses(parallels=processes):
                    return set[Action].union(*map(_gather_helper, processes))
                case Process(): raise TypeError(f"{p} may not be an abstract process.")

        for pa in self.process_assignments:
            actions = actions.union(_gather_helper(pa.process))

        return actions