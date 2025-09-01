"""
Evaluation of CCS Terms

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

import types

from dataclasses import dataclass

class Action(object):
    """
    Represents Actions of CCS Terms
    
    Actions consist of
    - a name (starting with a lowercase character)
    - a property whether or not they are of the dual kind (i.e. 'a)
    """

    NORMAL_FORM = False
    DUAL_FORM = True

    def __init__(self, name: str, is_dual: bool = NORMAL_FORM):
        self.name = name
        self.is_dual = is_dual

    def get_dual_action(self):
        return Action(self.name, not self.is_dual)
    
    def __repr__(self) -> str:
        return f"Action(name={self.name}, is_dual={self.is_dual})"

    def __str__(self) -> str:
        return ("'" if self.is_dual else "") + f"{self.name}"
    
    def __eq__(self, other: object) -> bool | types.NotImplementedType:
        if not isinstance(other, Action):
            return NotImplemented
            
        return self.name == other.name and self.is_dual == other.is_dual
    
class ActionSet(object):
    def __init__(self, actions: list[Action]):
        self.actions = actions

    def __eq__(self, other: object) -> bool | types.NotImplementedType:
        if not isinstance(other, ActionSet):
            return NotImplemented
            
        return all([
            (a == b) 
            for a, b 
            in zip(self.actions, other.actions, strict=True)]
        )
    
    def __repr__(self) -> str:
        return f"ActionSet(actions={self.actions})"

    def __str__(self) -> str:
        return "{" + ", ".join(map(str, self.actions)) + "}"
    
class NamedActionSet(object):
    def __init__(self, name: str, actionSet: ActionSet):
        self.name = name
        self.actionSet = actionSet

    def __eq__(self, other: object) -> bool | types.NotImplementedType:
        if not isinstance(other, NamedActionSet):
            return NotImplemented
            
        return self.name == other.name and self.actionSet == other.actionSet

class Process(object):
    pass

@dataclass(frozen=True)
class NilProcess(Process):    
    def __str__(self):
        return "0"
    
@dataclass(frozen=True)
class NamedProcess(Process):
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
    hiding: ActionSet | str
    
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
    name: NamedProcess
    process: Process

    def __str__(self) -> str:
        return f"{self.name} = {self.process};"