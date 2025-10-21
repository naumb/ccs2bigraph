"""
Translation of a CCS representation to a Bigraph representation
"""

from .ccs import representation as ccs
from .ccs.validation import FinitePureCcsValidatior 
from .bigraph import representation as big

class FiniteCcsTranslator(object):
    """
    Translation of Finite CCS into bigraphs
    """
    def __init__(self, ccs: ccs.CcsRepresentation) -> None:
        self._ccs = ccs
        self._big = None

    def _generate_ccs_controls(self) -> list[big.ControlDefinition]:
        """
        Includes the Bigraph Controls for CCS
        """

        return [
            big.ControlDefinition(big.AtomicControl("Nil", 0)),
            big.ControlDefinition(big.Control("Alt", 0)),
            big.ControlDefinition(big.Control("Send", 1)),
            big.ControlDefinition(big.Control("Get", 1)),
        ]

    def _generate_bigraph_content(self) -> None:
        """
        Applies the transformation ccs -> Bigraph transformation
        """
        def _translation_helper(current: ccs.Process) -> None:
            match current:
                case ccs.SumProcesses(sums=sums):
                    pass
                case ccs.NilProcess():
                    pass
                case ccs.ProcessByName():
                    pass
                case ccs.PrefixedProcess(prefix=prefix, remaining=remaining):
                    pass
                case ccs.HidingProcess(process=process, hiding=hiding):
                    pass
                case ccs.RenamingProcess(process=process, renaming=renaming):
                    pass
                case ccs.ParallelProcesses(parallels=parallels):
                    pass
                case ccs.Process(): raise TypeError(f"{current} may not be an abstract process.")

        # Initially, assert that
        # - there is only one process assignment
        # - the process is valid for pure finite ccs (i.e. all alternatives are prefix-guarded)

        assert len(self._ccs.process_assignments) == 1
        assert FinitePureCcsValidatior.validate(self._ccs)

        _translation_helper(self._ccs.process_assignments[0].process)

