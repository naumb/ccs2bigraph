"""
Translation of a CCS representation to a Bigraph representation
"""

from functools import reduce
from textwrap import dedent
from .ccs import representation as ccs
from .ccs.validation import FinitePureCcsValidatior 
from .ccs.augmentation import CcsAugmentor
from .bigraph import representation as big

class FiniteCcsTranslator(object):
    """
    Translation of Finite CCS into bigraphs
    """

    CCS_CONTROLS: list[big.ControlDefinition] = [
        big.ControlDefinition(big.Control("Ccs", 0)),
        big.ControlDefinition(big.Control("Execute", 0)),
        big.ControlDefinition(big.Control("Process", 1)),
        big.ControlDefinition(big.AtomicControl("Call", 1)),
        big.ControlDefinition(big.Control("Alt", 0)),
        big.ControlDefinition(big.Control("Send", 1)),
        big.ControlDefinition(big.Control("Get", 1)),
        big.ControlDefinition(big.AtomicControl("Nil", 0)),
    ]
    """
    The Bigraph Controls for CCS

    Besides 'Alt', 'Send', 'Get', and 'Nil' as defined by Millner, we introduced 'Ccs', 'Execute', 'Process', and 'Call' for named processes.
    """

    CCS_REACTION_RULES: list[big.BigraphReaction] = [
        big.BigraphReaction(
            "ccs_meta_call",
            dedent("""\
                Ccs.(Execute.Call{proc} | Process{proc}.id | id) 
                ->
                Ccs.(Execute.id | Process{proc}.id | id)
                @[0, 0, 1];
            """)
        ),
        big.BigraphReaction(
            "ccs_dual",
            dedent("""\
                Ccs.Execute.((Alt.(Send{action}.id | id)) | (Alt.(Get{action}.id | id)))
                ->
                Ccs.Execute.({action} | id | id)
                @[0, 2];
            """)
        ),
        big.BigraphReaction(
            "ccs_send",
            dedent("""\
                Ccs.Execute.((Alt.(Send{action}.id | id)) | id)
                ->
                Ccs.Execute.({action} | id | id)
                @[0, 2];
            """)
        ),
        big.BigraphReaction(
            "ccs_get",
            dedent("""\
                Ccs.Execute.((Alt.(Get{action}.id | id)) | id)
                ->
                Ccs.Execute.({action} | id | id)
                @[0, 2];
            """)
        ),
        big.BigraphReaction(
            "ccs_dual_hidden",
            dedent("""\
                /hidden Ccs.Execute.(Alt.(Send{hidden}.id | id)) | (Alt.(Get{hidden}.id | id))) | id)
                ->
                Ccs.Execute.(id | id) | id)
                @[0, 2, 4];
            """)
        ),
    ]
    """
    Includes the Bigraph Reaction rules for CCS

    Besides the rule "ccs_dual" for synchronizing actions as defined by Millner, we introduced the rules "ccs_send", "ccs_get", "ccs_dual_hidden". Further, we introduced the rule "ccs_meta_call" for "calling" named processes.
    """

    def __init__(self, ccs: ccs.CcsRepresentation, init_process: str) -> None:
        self._ccs = ccs
        self._ccs_actions = self._ccs.get_all_actions()
        self._init_bigraph = f"{init_process.lower()}_proc"

    def _bigraph_name_from_process_name(self, process_name: str) -> str:
        """
        Generates a bigraph name from a given process name

        :param str process_name: the process name to be translated
        :return str: the resulting bigraph name. Essentially, it is the lowercase process_name, appended by '_proc'
        """
        return f"{process_name.lower()}_proc"
    
    def _bigraph_assignment_name_from_process_name(self, process_name: str) -> str:
        """
        Generates a bigraph assignment name for a given process name

        :param str process_name: the process name to be used
        :return str: the resulting bigraph assignment name. Essentially, it is the `_bigraph_name_from_process_name`, appended by '_def'.
        """
        return f"{self._bigraph_name_from_process_name(process_name)}_def"
    
    def _generate_bigraph_assignment_from_process_assignment(self, process_assignment: ccs.ProcessAssignment) -> big.BigraphAssignment: 
        """
        Generates a bigraph assignment from a ccs process assignment.

        It will use `_bigraph_assignment_name_from_process_name` as the bigraph assignment name and `_bigraph_name_from_process_name` to refer to the process itself. Further, the resulting behavior will be nested in a `ControlByName('Process')` Control with a link to `_bigraph_name_from_process_name`

        :param ccs.ProcessAssignment process_assignment: The process assignment to be translated
        :return big.BigraphAssignment: The resulting translation. 
        """
        def _translation_helper(current: ccs.Process) -> big.Bigraph:
            match current:
                case ccs.NilProcess():
                    merging: list[big.Bigraph] = [big.IdleNameBigraph(big.Link(a.name)) for a in self._ccs_actions]
                    merging.append(big.ControlBigraph(big.ControlByName("Nil"), []))
                    return big.MergedBigraphs(merging)
                case ccs.ProcessByName(name=name):
                    # ProcessByName corresponds to a "call" to a process, hence represent it accordingly.
                    # Conveniently, together with the representation of ProcessAssignments, this also solves recursive calls
                    link = big.Link(f"{name.lower()}_proc")
                    return big.ControlBigraph(big.ControlByName("Call"), [link])
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

        return big.BigraphAssignment(
                self._bigraph_assignment_name_from_process_name(process_assignment.name),
                big.NestingBigraph(
                    big.ControlBigraph(big.ControlByName("Process"), [
                        big.Link(
                            self._bigraph_name_from_process_name(process_assignment.name)
                        )
                    ]),
                    _translation_helper(process_assignment.process)
                )
            ) 
    
    def _generate_bigraph_content(self) -> list[big.BigraphAssignment]:
        """
        Applies the Ccs -> Bigraph transformation
        """
        
        # Initially, assert that
        # - there is at least one process to be translated
        # - the process is valid for pure finite ccs (i.e. all alternatives are prefix-guarded)

        if not len(self._ccs.process_assignments) >= 1:
            raise ValueError("No processes defined.")
        if not FinitePureCcsValidatior.validate(self._ccs):
            raise ValueError("Invalid Processes. TODO: Which?")

        bigraph_assignments = [
            self._generate_bigraph_assignment_from_process_assignment(pa)
            for pa in self._ccs.process_assignments
        ]

        # Append template for initial bigraph, essentially "calling" the corresponding process
        result = bigraph_assignments + [self._generate_init_bigraph(bigraph_assignments)]

        return result
    
    def _generate_init_bigraph(self, bigraph_assignments: list[big.BigraphAssignment]) -> big.BigraphAssignment:

        merging_wrapper: list[big.Bigraph] = [
            big.NestingBigraph(
                big.ControlBigraph(big.ControlByName("Execute"), []),
                big.ControlBigraph(big.ControlByName("Call"), [big.Link(self._init_bigraph)])
            ),
        ]

        bigraphs_by_name: list[big.Bigraph] = [
            big.BigraphByName(ba.name) 
            for ba in bigraph_assignments
        ]

        merging = merging_wrapper + bigraphs_by_name

        return big.BigraphAssignment(
            "start",
            big.NestingBigraph(
                big.ControlBigraph(
                    big.ControlByName("Ccs"), [],
                ),
                big.MergedBigraphs(merging)
            )
        )

    def translate(self) -> big.BigraphRepresentation:
        for pa in self._ccs.process_assignments:
            pa.process = CcsAugmentor.augment(pa.process)

        return big.BigraphRepresentation(
            self.CCS_CONTROLS,
            self._generate_bigraph_content(),
            self.CCS_REACTION_RULES,
        )
