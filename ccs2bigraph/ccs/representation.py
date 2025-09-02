"""
Representation of CCS Terms

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

from dataclasses import dataclass

@dataclass(frozen=True)
class Action(object):
    """
    Represents Actions of CCS Terms
    
    Actions consist of
    - a name (starting with a lowercase character)
    - a property whether or not they are of the dual kind (i.e. 'a)
    """

    NORMAL_FORM = False
    DUAL_FORM = True

    name: str
    is_dual: bool = NORMAL_FORM

    def get_dual_action(self):
        return Action(self.name, not self.is_dual)

    def __str__(self) -> str:
        return ("'" if self.is_dual else "") + f"{self.name}"

@dataclass(frozen=True)
class ActionSet(object):
    actions: list[Action]

    def __str__(self) -> str:
        return "{" + ", ".join(map(str, self.actions)) + "}"
    
@dataclass(frozen=True)
class ActionSetByName(object):
    name: str

@dataclass(frozen=True)
class ActionSetAssignment(object):
    name: str
    actionSet: ActionSet

    def __str__(self) -> str:
        return f"{self.name} = {self.actionSet};"

class Process(object):
    pass

@dataclass(frozen=True)
class NilProcess(Process):    
    def __str__(self):
        return "0"
    
@dataclass(frozen=True)
class ProcessByName(Process):
    name: str
    
    def __str__(self):
        return self.name

@dataclass(frozen=True)
class PrefixedProcess(Process):
    prefix: Action
    remaining: Process
    
    def __str__(self) -> str:
        return f"({self.prefix}.{self.remaining})"

@dataclass(frozen=True)
class HidingProcess(Process):
    process: Process
    hiding: ActionSet | ActionSetByName
    
    def __str__(self) -> str:
        return f"({self.process} \\ {self.hiding})"

@dataclass(frozen=True)
class RenamingProcess(Process):
    process: Process
    renaming: list[tuple[Action, Action]]

    def __str__(self) -> str:
        return f"({self.process}[" + ", ".join(f"{new}/{old}" for (new, old) in self.renaming) + "])"

@dataclass(frozen=True)
class AlternativeProcesses(Process):
    alternatives: list[Process]
    
    def __str__(self) -> str:
        return "(" + " + ".join(map(str, self.alternatives)) + ")"

@dataclass(frozen=True)
class ParallelProcesses(Process):
    parallels: list[Process]
    
    def __str__(self) -> str:
        return "(" + " | ".join(map(str, self.parallels)) + ")"
    
@dataclass(frozen=True)
class ProcessAssignment:
    name: str
    process: Process

    def __str__(self) -> str:
        return f"{self.name} = {self.process};"
    
@dataclass(frozen=True)
class Ccs:
    processes: list[ProcessAssignment]
    sets: list[ActionSetAssignment]