"""
Algebraic Representation of bigraphs (c.f. BigraphER syntax)

This file provides classes for the individual parts of algebraic Bigraph terms, i.e.
- controls
    - atomic
    - non-atomic
- bigraph expressions, consisting of
    - `1`
    - id
    - closing
    - nesting
    - parallel product
    - merging
"""

import logging
logger = logging.getLogger(__name__)

from abc import ABC
from dataclasses import dataclass

@dataclass(frozen=True)
class Control(object):
    """
    Representation of the control of Bigraph nodes

    :param str name: The name of the control (i.e. not the corresponding node)
    :param int arity: The number of ports of the control
    """

    name: str
    arity: int

@dataclass(frozen=True)
class AtomicControl(Control):
    """
    Representation of an atomic control of Bigraph nodes

    :param str name: The name of the control (i.e. not the corresponding node)
    :param int arity: The number of ports of the control
    """
    
@dataclass(frozen=True)
class ControlByName(object):
    """
    Refers to an `Control` by its name.

    :param str name: Name of the referenced `Control`
    
    Example:
    >>> str(ControlByName("A"))
    'A'
    """

    name: str

    def __str__(self) -> str:
        return self.name
    
@dataclass(frozen=True)
class ControlDefinition(object):
    """
    Refers to a definition of a control

    :param Control control: The Control to be defined

    Example:
    >>> str(ControlDefinition(Control("A", 3)))
    'ctrl A = 3;'
    >>> str(ControlDefinition(AtomicControl("B", 42)))
    'atomic ctrl B = 42;'
    """

    control: Control

    def __str__(self) -> str:
        if isinstance(self.control, AtomicControl):
            return f"atomic ctrl {self.control.name} = {self.control.arity};"
        else:
            return f"ctrl {self.control.name} = {self.control.arity};"

    
@dataclass(frozen=True)
class Link(object):
    """
    Representation of a single link in the bigraph

    :param str name: The name of the link

    Example:
    >>> str(Link("a"))
    'a'
    """

    name: str

    def __str__(self) -> str:
        return f"{self.name}"

class Bigraph(ABC):
    """
    Abstract Base Class for Bigraph definitions
    """
    pass

@dataclass(frozen=True)
class OneBigraph(Bigraph):
    """
    The Place(graph) 1

    Example
    >>> str(OneBigraph())
    '1'
    """
    def __str__(self) -> str:
        return "1"
    
@dataclass(frozen=True)
class IdBigraph(Bigraph):
    """
    The Place(graph) id

    Example
    >>> str(IdBigraph())
    'id'
    """
    def __str__(self) -> str:
        return "id"
    
@dataclass(frozen=True)
class ControlBigraph(Bigraph):
    """
    A Bigraph consisting of a single node of a certain control

    :param Control control: The control of the node
    :param list[str] links: The links associated to the individual ports

    Example:
    >>> str(ControlBigraph("A", [Link('a'), Link('b'), Link('c')]))
    'A{a,b,c}'
    """
    control: ControlByName
    links: list[Link]

    def __str__(self) -> str:
        l = ""
        if len(self.links) > 0:
            l = "{" + ",".join(map(str, self.links)) + "}"
        return f"{self.control}{l}"

    
@dataclass(frozen=True)
class ClosedBigraph(Bigraph):
    """
    A Bigraph resulting from the closing of a link (/x B)

    :param str link: The closed link
    :param Bigraph bigraph: The :class:`Bigraph` of which the link is closed
    """

    link: Link
    bigraph: Bigraph

    def __str__(self) -> str:
        return f"(/{self.link} {self.bigraph})"
    
@dataclass(frozen=True)
class NestingBigraph(Bigraph):
    """
    A Bigraph resulting from the nesting operation

    :param ControlBigraph | IdBigraph control: The Bigraph which corresponds to the outer node
    :param Bigraph inner: The inner bigraph which is nested inside the outer node 

    Example:
    >>> str(NestingBigraph(ControlBigraph(ControlByName("A"), [Link("a")]), IdBigraph()))
    '(A{a}.id)'
    """

    control: ControlBigraph | IdBigraph
    inner: Bigraph

    def __str__(self) -> str:
        return f"({self.control}.{self.inner})"

    
@dataclass(frozen=True)
class MergedBigraphs(Bigraph):
    """
    A Bigraph resulting from the application of the merging operator (A | B)

    :param list[Bigraph] merging: The merged Bigraphs
    """
    merging: list[Bigraph]

    def __str__(self) -> str:
        return "(" + " | ".join(map(str, self.merging)) + ")"
    
@dataclass(frozen=True)
class ParallelBigraphs(Bigraph):
    """
    A Bigraph resulting from the application of the parallel product operator (A || B)

    :param list[Bigraph] parallel: The parallel Bigraphs
    """
    parallel: list[Bigraph]

    def __str__(self) -> str:
        return "(" + " | ".join(str(self.parallel)) + ")"

@dataclass(frozen=True)
class BigraphAssignment(object):
    """
    Assignment of a :class:`Bigraph` to a name.

    :param str name: The name to which the bigraph is assigned
    :param Bigraph bigraph: The actual bigraph.
    """

    name: str
    bigraph: Bigraph

    def __str__(self) -> str:
        return f"big {self.name} = {self.bigraph};"

@dataclass(frozen=True)
class BigraphByName(object):
    """
    Refers to an :class:`BigraphAssignment` by its name.

    :param str name: Name of the referenced `BigraphAssignment`
    
    Example:
    >>> str(BigraphByName("A"))
    'A'
    """
    name: str
    
    def __str__(self):
        return self.name

