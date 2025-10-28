"""Bigraph Validation Tests"""

from ccs2bigraph.ccs.augmentation import CcsAugmentor
from ccs2bigraph.ccs.validation import *
from ccs2bigraph.ccs.representation import *

def helper_wrap_process(p: Process) -> CcsRepresentation:
    return CcsRepresentation([
        ProcessAssignment("Test", p)
    ], [])

class Test_Simple_Finite_Pure_Ccs_Validation():
    def test_nil_process_validation(self):
        assert FinitePureCcsValidatior.validate(helper_wrap_process(NilProcess())) == True

    def test_process_by_name_validation(self):
        assert FinitePureCcsValidatior.validate(helper_wrap_process(ProcessByName("Test"))) == True

    def test_prefixed_process_validation(self):
        inp = PrefixedProcess(Action("a"), NilProcess())
        assert FinitePureCcsValidatior.validate(helper_wrap_process(inp)) == False

    def test_wrapped_prefixed_process_validation(self):
        inp = SumProcesses([PrefixedProcess(Action("a"), NilProcess())])
        inp.sums[0].parent = inp

        assert FinitePureCcsValidatior.validate(helper_wrap_process(inp)) == True

    def test_hiding_process_actionset_validation(self):
        inp = HidingProcess(ProcessByName("A"), ActionSet(list(map(Action, ["a", "b"]))))
        assert FinitePureCcsValidatior.validate(helper_wrap_process(inp)) == True

    def test_hiding_process_actionsetbyname_validation(self):
        inp = HidingProcess(ProcessByName("A"), ActionSetByName("H"))
        assert FinitePureCcsValidatior.validate(helper_wrap_process(inp)) == True

    def test_renaming_process_validation(self):
        inp = RenamingProcess(ProcessByName("A"), [(Action("new"), Action("old"))])
        assert FinitePureCcsValidatior.validate(helper_wrap_process(inp)) == True

    def test_sum_processes_failed_validation(self):
        inp = SumProcesses([NilProcess(), ProcessByName("A")])
        assert FinitePureCcsValidatior.validate(helper_wrap_process(inp)) == False

    def test_sum_processes_successful_validation(self):
        inp = (SumProcesses([PrefixedProcess(Action("x"), NilProcess()), PrefixedProcess(DualAction("x"), NilProcess())]))
        
        # reconstruct parent relationship
        for s in inp.sums:
            s.parent = inp
        
        assert FinitePureCcsValidatior.validate(helper_wrap_process(inp)) == True

    def test_parallel_processes_validation(self):
        inp = ParallelProcesses([NilProcess(), ProcessByName("A")])
        assert FinitePureCcsValidatior.validate(helper_wrap_process(inp)) == True


class Test_Complex_Bigraph_Validation():
    def test_sum_validation(self):
        inp = SumProcesses(
            [
                PrefixedProcess(
                    Action("a"),
                    SumProcesses([
                        PrefixedProcess(
                            DualAction("b"),
                            ProcessByName("One"),
                        ),
                    ]),
                ),
                PrefixedProcess(
                    DualAction("a"),
                    SumProcesses([
                        PrefixedProcess(
                            Action("b"), 
                            ProcessByName("Two"),
                        ),
                    ]),
                )
            ]
        )

        inp = CcsAugmentor.augment(inp)

        assert FinitePureCcsValidatior.validate(helper_wrap_process(inp)) == True

    def test_complex_process_A_failed_validation(self):
        inp = ParallelProcesses(
            [
                SumProcesses(
                    [
                        RenamingProcess( # Failure will occur here
                            PrefixedProcess(
                                Action("a"),
                                PrefixedProcess(
                                    DualAction("b"),
                                    ProcessByName("One"),
                                ),
                            ),
                            [(Action("x"), Action("y"))],
                        ),
                        HidingProcess( # Failure will occur here
                            PrefixedProcess(
                                DualAction("a"),
                                PrefixedProcess(
                                    Action("b"),
                                    RenamingProcess(
                                        ProcessByName("Two"),
                                        [(Action("x"), Action("y"))],
                                    ),
                                ),
                            ),
                            ActionSetByName("L"),
                        ),
                    ]
                ),
                HidingProcess(
                    RenamingProcess(
                        SumProcesses(
                            [
                                PrefixedProcess(
                                    Action("x"),
                                    PrefixedProcess(
                                        Action("y"),
                                        PrefixedProcess(
                                            Action("z"),
                                            ProcessByName("Test"),
                                        ),
                                    ),
                                ),
                                ParallelProcesses( # Failure will occur here!
                                    [
                                        PrefixedProcess(
                                            DualAction("a"),
                                            PrefixedProcess(
                                                DualAction("b"),
                                                NilProcess(),
                                            ),
                                        ),
                                        PrefixedProcess(
                                            Action("a"),
                                            PrefixedProcess(
                                                Action("b"),
                                                ProcessByName("A"),
                                            ),
                                        ),
                                    ]
                                ),
                            ]
                        ),
                        [
                            (Action("a"), Action("b")),
                            (Action("b"), Action("a")),
                            (Action("x"), Action("x")),
                        ],
                    ),
                    ActionSet(list(map(Action, ["a", "b", "c"]))),
                ),
            ]
        )
        assert FinitePureCcsValidatior.validate(helper_wrap_process(inp)) == False

    def test_complex_process_A_successful_validation(self):
        inp = ParallelProcesses(
            [
                SumProcesses(
                    [
                        PrefixedProcess(
                            Action("a"),
                            RenamingProcess(
                                PrefixedProcess(
                                    DualAction("b"),
                                    ProcessByName("One"),
                                ),
                                [(Action("x"), Action("y"))],
                            ),
                        ),
                        PrefixedProcess(
                            DualAction("a"),
                            HidingProcess(
                                PrefixedProcess(
                                    Action("b"),
                                    RenamingProcess(
                                        ProcessByName("Two"),
                                        [(Action("x"), Action("y"))],
                                    ),
                                ),
                                ActionSetByName("L"),
                            ),
                        ),
                    ]
                ),
                HidingProcess(
                    RenamingProcess(
                        SumProcesses(
                            [
                                PrefixedProcess(
                                    Action("x"),
                                    PrefixedProcess(
                                        Action("y"),
                                        PrefixedProcess(
                                            Action("z"),
                                            ProcessByName("Test"),
                                        ),
                                    ),
                                ),
                                PrefixedProcess(
                                    Action("y"),
                                    ParallelProcesses(
                                        [
                                            PrefixedProcess(
                                                DualAction("a"),
                                                PrefixedProcess(
                                                    DualAction("b"),
                                                    NilProcess(),
                                                ),
                                            ),
                                            PrefixedProcess(
                                                Action("a"),
                                                PrefixedProcess(
                                                    Action("b"),
                                                    ProcessByName("A"),
                                                ),
                                            ),
                                        ]
                                    ),
                                ),
                            ]
                        ),
                        [
                            (Action("a"), Action("b")),
                            (Action("b"), Action("a")),
                            (Action("x"), Action("x")),
                        ],
                    ),
                    ActionSet(list(map(Action, ["a", "b", "c"]))),
                ),
            ]
        )

        # Use Augmentation here, even if this is a bit fuzzy
        inp = CcsAugmentor.augment(inp)

        assert FinitePureCcsValidatior.validate(helper_wrap_process(inp)) == True
