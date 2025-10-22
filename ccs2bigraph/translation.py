"""
Translation of a CCS representation to a Bigraph representation
"""

from functools import reduce
from textwrap import dedent
from .ccs import representation as ccs
from .ccs.validation import FinitePureCcsValidatior 
from .ccs.augmentation import CcsAugmentator
from .bigraph import representation as big

class FiniteCcsTranslator(object):
    """
    Translation of Finite CCS into bigraphs
    """
    def __init__(self, ccs: ccs.CcsRepresentation) -> None:
        self._ccs = ccs
        self._ccs_actions = self._ccs.get_all_actions()

    def _generate_ccs_controls(self) -> list[big.ControlDefinition]:
        """
        Includes the Bigraph Controls for CCS
        """

        return [
            big.ControlDefinition(big.Control("Ccs", 0)),
            big.ControlDefinition(big.AtomicControl("Nil", 0)),
            big.ControlDefinition(big.Control("Alt", 0)),
            big.ControlDefinition(big.Control("Send", 1)),
            big.ControlDefinition(big.Control("Get", 1)),
        ]
    
    def _generate_bigraph_reactions(self) -> list[big.BigraphReaction]:
        """
        Includes the Bigraph Reaction rules for CCS
        """
        return [
            big.BigraphReaction(
                "ccs_react",
                dedent("""\
                    Ccs.((Alt.(Send{action}.id | id)) | (Alt.(Get{action}.id | id)))
                    ->
                    Ccs.({action} | id | id)
                    @[0, 2];
                """)
            ),
            big.BigraphReaction(
                "ccs_send",
                dedent("""\
                    Ccs.((Alt.(Send{action}.id | id)) | id)
                    ->
                    Ccs.({action} | id | id)
                    @[0, 2];
                """)
            ),
            big.BigraphReaction(
                "ccs_get",
                dedent("""\
                    Ccs.((Alt.(Get{action}.id | id)) | id)
                    ->
                    Ccs.({action} | id | id)
                    @[0, 2];
                """)
            ),
        ]

    def _generate_bigraph_content(self) -> list[big.BigraphAssignment]:
        """
        Applies the Ccs -> Bigraph transformation
        """
        def _translation_helper(current: ccs.Process) -> big.Bigraph:
            match current:
                case ccs.NilProcess():
                    merging: list[big.Bigraph] = [big.IdleNameBigraph(big.Link(a.name)) for a in self._ccs_actions]
                    merging.append(big.ControlBigraph(big.ControlByName("Nil"), []))
                    return big.MergedBigraphs(merging)
                case ccs.ProcessByName():
                    return big.BigraphByName(str(current))
                case ccs.PrefixedProcess(prefix=prefix, remaining=remaining):
                    if isinstance(prefix, ccs.DualAction):
                        ctrl = big.ControlBigraph(big.ControlByName("Send"), [big.Link(prefix.name)])
                    else:
                        ctrl = big.ControlBigraph(big.ControlByName("Get"), [big.Link(prefix.name)])

                    return big.NestingBigraph(ctrl, _translation_helper(remaining))
                case ccs.HidingProcess(process=process, hiding=hiding):
                    # Infer actual actionSet behind hiding
                    if isinstance(hiding, ccs.ActionSetByName):
                        # Filter out all action sets with the matching name
                        action_sets = list(filter(lambda a: a.name == hiding.name, self._ccs.action_set_assignments))
                        
                        if len(action_sets) > 1:
                            raise ValueError("ActionSet is defined multiple times")
                        if len(action_sets) == 0:
                            raise ValueError("ActionSet is undefined")
                        
                        actions = action_sets[0].actionSet.actions
                    else: actions = hiding.actions

                    # Create Links from actions
                    links = map(big.Link, [a.name for a in actions])

                    # Helper function to swap parameters of big.ClosedBigraph
                    def _closed_helper(b: big.Bigraph, l: big.Link) -> big.Bigraph:
                        return big.ClosedBigraph(l, b) #type: ignore

                    # Create C(L, C(L, C(L, _t(p)))) form by folding/reducing
                    return reduce(_closed_helper, links, _translation_helper(process))
                case ccs.RenamingProcess(process=process, renaming=renaming):  # pyright: ignore[reportUnusedVariable]
                    # Problem with Renaming: we don't know which actions to rename yet.
                    # Also, we cannot rename all following actions on process level here, since we do not know which actions to rename.
                    raise RuntimeError("NYI")
                case ccs.ParallelProcesses(parallels=parallels):
                    return big.MergedBigraphs(list(map(_translation_helper, parallels)))
                case ccs.SumProcesses(sums=sums):
                    return big.NestingBigraph(
                        big.ControlBigraph(big.ControlByName("Alt"), []),
                        big.MergedBigraphs(list(map(_translation_helper, sums)))
                    )
                case ccs.Process(): raise TypeError(f"{current} may not be an abstract process.")

        # Initially, assert that
        # - the process is valid for pure finite ccs (i.e. all alternatives are prefix-guarded)

        if not len(self._ccs.process_assignments) >= 1:
            raise ValueError("No processes defined.")
        if not FinitePureCcsValidatior.validate(self._ccs):
            raise ValueError("Invalid Processes. TODO: Which?")

        result = [
            # Keep in mind: Bigraph identifiers must be lowercase names
            big.BigraphAssignment(pa.name.lower(), _translation_helper(pa.process)) 
            for pa in self._ccs.process_assignments
        ]

        return result

    def translate(self, init_process: str) -> big.BigraphRepresentation:
        for pa in self._ccs.process_assignments:
            pa.process = CcsAugmentator.augment(pa.process)

        return big.BigraphRepresentation(
            self._generate_ccs_controls(),
            self._generate_bigraph_content(),
            big.BigraphByName(init_process.lower()),
            self._generate_bigraph_reactions(),
        )
