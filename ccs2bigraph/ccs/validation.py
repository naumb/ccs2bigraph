"""
Validation of CCS Processes
"""
import logging
logger = logging.getLogger(__name__)

from .representation import *

class FinitePureCcsValidatior(object):
    """
    Checks whether or not a given :class:`CcsRepresentation` is formed from pure finite ccs.

    Conceputally, this means that all Alternatives (so they occur) have to be guarded
    """

    @staticmethod
    def validate(ccs: CcsRepresentation) -> bool:
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
                    # Check whether all children are prefixed
                    if not all([isinstance(s, PrefixedProcess) for s in sums]): 
                        raise ValueError("Unguarded child in Sum!", p)
                    
                    return all(map(_traverse_helper, sums))
                
                case NilProcess(): 
                    # Correct by definition
                    return True
                
                case ProcessByName(): 
                    # TODO: is this correct?
                    return True
                
                case PrefixedProcess(prefix=_, remaining=r): 
                    # Check if parent is a SumProcess
                    if not isinstance(p.parent, SumProcesses): 
                        raise ValueError("Prefix without Sum-parent!", p)
                    
                    # Check remaining process after prefix
                    return _traverse_helper(r)
                
                case HidingProcess(process=p, hiding=_): 
                    # No errors possible, check remaining process
                    return _traverse_helper(p)
                
                case RenamingProcess(process=p, renaming=_): 
                    # No errors possible, check remaining process
                    return _traverse_helper(p)
                
                case ParallelProcesses(parallels=ps): 
                    return all(map(_traverse_helper, ps))
                
                case Process(): 
                    raise TypeError(f"{p} may not be an abstract process.")
        
        # All Checks passed
        return all(map(_traverse_helper, [pa.process for pa in ccs.process_assignments]))