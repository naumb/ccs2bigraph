"""
Validation of CCS Processes
"""

from .representation import *

import logging
logger = logging.getLogger(__name__)

class FinitePureCcsValidatior(object):
    """
    Checks whether or not a given :class:`CcsRepresentation` is formed from pure finite ccs.

    Conceputally, this means that all Alternatives (so they occur) have to be guarded
    """

    @staticmethod
    def validate(ccs: CcsRepresentation):
        """
        Static method to execute the validation check

        :param CcsRepresentation ccs: CCS to check finity and pureness (i.e. whether or not all alternatives are guarded)
        """

        def _traverse_helper(p: Process) -> bool:
            """
            Returns whether or not the current process :param:`p` is valid

            :param Process p: The process to be validated
            :return bool: Whether or not it is valid
            """
            match p:
                case SumProcesses(sums=sums):
                    return all([(isinstance(s, PrefixedProcess) and _traverse_helper(s)) for s in sums])
                case NilProcess(): return True
                case ProcessByName(): return True #TODO: is this correct?
                case PrefixedProcess(prefix=_, remaining=p): return isinstance(p.parent, SumProcesses) and _traverse_helper(p)
                case HidingProcess(process=p, hiding=_): return _traverse_helper(p)
                case RenamingProcess(process=p, renaming=_): return _traverse_helper(p)
                case ParallelProcesses(parallels=ps): return all(_traverse_helper(p) for p in ps)
                case Process(): return False # This should not occur.

        return all(_traverse_helper(p) for p in [pa.process for pa in ccs.process_assignments])