"""
Augmentation of CCS Processes

It serves two main purposes:
- It "fixes" the parent relation of the :class:`Process`.
- It introduces instances of :class:`SumProcess` as parents of :class:`PrefixedProcess` where necessary
"""

from .representation import *

import copy

class CcsAugmentator(object):
    """
    Wrapper class for Augmentation
    """

    @staticmethod
    def _augment_parents(process: Process) -> Process:
        """
        Static method to add the parent relation for each childprocess

        :param Process process: The process to augment
        """
        def _traverse_helper(current: Process):
            match current:
                case NilProcess() | ProcessByName(): return # Nil has no children, TODO: Is this correct for ProcessByName?
                case SumProcesses(sums=children) | ParallelProcesses(parallels=children):
                    for child in children:
                        child.parent = current
                        _traverse_helper(child)
                case PrefixedProcess(prefix=_, remaining=child) \
                   | HidingProcess(process=child, hiding=_) \
                   | RenamingProcess(process=child, renaming=_):
                    child.parent = current
                    _traverse_helper(child)
                case Process(): raise ValueError("Process may never be instantiated directly")
        
        c = copy.deepcopy(process)
        _traverse_helper(c)
        return c
        

    @staticmethod
    def _augment_prefixes(process: Process) -> Process:
        """
        Static method to add missing :class:`SumProcess` instances as parents of :class:`PrefixProcesses`

        :param Process process: The process to augment
        """
        def _traverse_helper(current: Process) -> Process:
            match current:
                case NilProcess() | ProcessByName(): 
                    return current # Nil has no children, TODO: Is this correct for ProcessByName?
                case SumProcesses(parent=parent, sums=children):
                    replacement = SumProcesses(list(map(_traverse_helper, children)))
                    replacement.parent = parent
                    return replacement
                case ParallelProcesses(parent=parent, parallels=children):
                    replacement = ParallelProcesses(list(map(_traverse_helper, children)))
                    replacement.parent = parent
                    return replacement
                case HidingProcess(parent=parent, process=child, hiding=hiding):
                    replacement = HidingProcess(_traverse_helper(child), hiding)
                    replacement.parent = parent
                    return replacement
                case RenamingProcess(parent=parent, process=child, renaming=renaming):
                    replacement = RenamingProcess(_traverse_helper(child), renaming)
                    replacement.parent = parent
                    return replacement
                case PrefixedProcess(parent=parent, prefix=prefix, remaining=child):
                    replacement = PrefixedProcess(prefix, _traverse_helper(child))

                    if not isinstance(parent, SumProcesses):
                        wrapper = SumProcesses([replacement])
                        replacement.parent = wrapper # pyright: ignore[reportAttributeAccessIssue]
                        wrapper.parent = parent # pyright: ignore[reportAttributeAccessIssue]
                        return wrapper 
                    else:
                        replacement.parent = parent
                        return replacement
                    
                case Process(): raise ValueError("Process may never be instantiated directly")

        return _traverse_helper(process)
    
    @staticmethod
    def augment(process: Process) -> Process:
        return CcsAugmentator._augment_prefixes(CcsAugmentator._augment_parents(process))