"""CCS Grammar Tests"""

import pyparsing as pp
import pathlib

import pytest

import ccs2bigraph.ccs.grammar as g
from ccs2bigraph.ccs.representation import *

class Test_Action():
    def test_simple_action(self):
        inp = "a"
        exp = Action("a")
        act = g._action.parse_string(inp)[0]  # type: ignore (testing private member)
        assert exp == act

    def test_dual_action(self):
        inp = "'a"
        exp = DualAction("a")
        act = g._action.parse_string(inp)[0]  # type: ignore (testing private member)
        assert exp == act

    def test_long_action(self):
        inp = "areallylongactionname"
        exp = Action("areallylongactionname")
        act = g._action.parse_string(inp)[0]  # type: ignore (testing private member)
        assert exp == act

    def test_action_with_whitespace(self):
        inp = "  a  "
        exp = Action("a")
        act = g._action.parse_string(inp)[0]  # type: ignore (testing private member)
        assert exp == act

    def test_action_with_uppercase(self):
        inp = "aBcDe"
        exp = Action("aBcDe")
        act = g._action.parse_string(inp)[0]  # type: ignore (testing private member)
        assert exp == act

    def test_invalid_action_name(self):
        inp = "Invalid"

        with pytest.raises(pp.exceptions.ParseException):
            g._action.parse_string(inp)  # type: ignore (testing private member)

class Test_Set():
    def test_simple_set(self):
        inp = "{a}"
        exp = ActionSet([Action("a")])
        act = g._actionset.parse_string(inp)[0]  # type: ignore (testing private member)
        assert exp == act

    def test_long_set(self):
        inp = "{a, b, c, d}"
        exp = ActionSet(list(map(Action, ["a", "b", "c", "d"])))
        act = g._actionset.parse_string(inp)[0]  # type: ignore (testing private member)
        assert exp == act

    def test_set_assignment(self):
        inp = "set Test = {a, b, c, d};"
        exp = ActionSetAssignment(
            "Test", ActionSet(list(map(Action, ["a", "b", "c", "d"])))
        )
        act = g._actionset_assignment.parse_string(inp)[0]  # type: ignore (testing private member)
        assert exp == act

    def test_weirdly_named_actionset_bang(self):
        inp = r"set A! = {a};"
        exp = CcsRepresentation([], [ActionSetAssignment("A!", ActionSet([Action("a")]))])
        act = g.parse(inp)
        assert exp == act
    
    def test_weirdly_named_actionset_hash(self):
        inp = r"set A# = {a};"
        exp = CcsRepresentation([], [ActionSetAssignment("A#", ActionSet([Action("a")]))])
        act = g.parse(inp)
        assert exp == act
    
    def test_weirdly_named_actionset_prime(self):
        inp = r"set A' = {a};"
        exp = CcsRepresentation([], [ActionSetAssignment("A'", ActionSet([Action("a")]))])
        act = g.parse(inp)
        assert exp == act
    
    def test_weirdly_named_actionset_dash(self):
        inp = r"set A- = {a};"
        exp = CcsRepresentation([], [ActionSetAssignment("A-", ActionSet([Action("a")]))])
        act = g.parse(inp)
        assert exp == act
    
    def test_weirdly_named_actionset_qm(self):
        inp = r"set A? = {a};"
        exp = CcsRepresentation([], [ActionSetAssignment("A?", ActionSet([Action("a")]))])
        act = g.parse(inp)
        assert exp == act
    
    def test_weirdly_named_actionset_circumflex(self):
        inp = r"set A^ = {a};"
        exp = CcsRepresentation([], [ActionSetAssignment("A^", ActionSet([Action("a")]))])
        act = g.parse(inp)
        assert exp == act
    
    def test_weirdly_named_actionset_underscore(self):
        inp = r"set A_ = {a};"
        exp = CcsRepresentation([], [ActionSetAssignment("A_", ActionSet([Action("a")]))])
        act = g.parse(inp)
        assert exp == act

class Test_Simple_Grammar():
    def test_simple_process(self):
        inp = "A = 0;"
        exp = CcsRepresentation([ProcessAssignment("A", NilProcess())], [])
        act = g.parse(inp)
        assert exp == act

    def test_simple_prefixed_process(self):
        inp = "A = a.0;"
        exp = CcsRepresentation(
            [
                ProcessAssignment(
                    "A", PrefixedProcess(Action("a"), NilProcess())
                )
            ],
            [],
        )
        act = g.parse(inp)
        assert exp == act

    def test_dual_prefixed_process(self):
        inp = "A = 'a.0;"
        exp = CcsRepresentation(
            [
                ProcessAssignment(
                    "A",
                    PrefixedProcess(
                        DualAction("a"), NilProcess()
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        assert exp == act

    def test_simple_alternative_process(self):
        inp = "A = a.0 + b.0;"
        exp = CcsRepresentation(
            [
                ProcessAssignment(
                    "A",
                    SumProcesses(
                        [
                            PrefixedProcess(Action("a"), NilProcess()),
                            PrefixedProcess(Action("b"), NilProcess()),
                        ]
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        assert exp == act

    def test_dual_alternative_process(self):
        inp = "A = a.0 + 'b.0;"
        exp = CcsRepresentation(
            [
                ProcessAssignment(
                    "A",
                    SumProcesses(
                        [
                            PrefixedProcess(Action("a"), NilProcess()),
                            PrefixedProcess(
                                DualAction("b"), NilProcess()
                            ),
                        ]
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        assert exp == act

    def test_simple_parallel_process(self):
        inp = "A = a.0 | b.0;"
        exp = CcsRepresentation(
            [
                ProcessAssignment(
                    "A",
                    ParallelProcesses(
                        [
                            PrefixedProcess(Action("a"), NilProcess()),
                            PrefixedProcess(Action("b"), NilProcess()),
                        ]
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        assert exp == act

    def test_dual_parallel_process(self):
        inp = "A = 'a.0 | b.0;"
        exp = CcsRepresentation(
            [
                ProcessAssignment(
                    "A",
                    ParallelProcesses(
                        [
                            PrefixedProcess(
                                DualAction("a"), NilProcess()
                            ),
                            PrefixedProcess(Action("b"), NilProcess()),
                        ]
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        assert exp == act

    def test_simple_hiding_process(self):
        inp = r"A = a.0 \ {a, b};"
        exp = CcsRepresentation(
            [
                ProcessAssignment(
                    "A",
                    PrefixedProcess(
                        Action("a"),
                        HidingProcess(
                            NilProcess(), ActionSet([Action("a"), Action("b")])
                        ),
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        assert exp == act

    def test_dual_hiding_process(self):
        inp = r"A = ('a.0) \ {a, b};"
        exp = CcsRepresentation(
            [
                ProcessAssignment(
                    "A",
                    HidingProcess(
                        PrefixedProcess(
                            DualAction("a"), NilProcess()
                        ),
                        ActionSet([Action("a"), Action("b")]),
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        assert exp == act

    def test_ref_hiding_process(self):
        inp = r"A = ('a.0) \ H;"
        exp = CcsRepresentation(
            [
                ProcessAssignment(
                    "A",
                    HidingProcess(
                        PrefixedProcess(
                            DualAction("a"), NilProcess()
                        ),
                        ActionSetByName("H"),
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        assert exp == act

    def test_simple_renaming_process(self):
        inp = r"A = a.0[b/a];"
        exp = CcsRepresentation(
            [
                ProcessAssignment(
                    "A",
                    PrefixedProcess(
                        Action("a"),
                        RenamingProcess(
                            NilProcess(), [(Action("b"), Action("a"))]
                        ),
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        assert exp == act

    def test_long_renaming_process(self):
        inp = r"A = (a.0)[b/a, d/c, f/e];"
        exp = CcsRepresentation(
            [
                ProcessAssignment(
                    "A",
                    RenamingProcess(
                        PrefixedProcess(Action("a"), NilProcess()),
                        [
                            (Action("b"), Action("a")),
                            (Action("d"), Action("c")),
                            (Action("f"), Action("e")),
                        ],
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        assert exp == act

    def test_weirdly_named_process_bang(self):
        inp = r"A! = 0;"
        exp = CcsRepresentation([ProcessAssignment("A!", NilProcess())], [])
        act = g.parse(inp)
        assert exp == act
    
    def test_weirdly_named_process_hash(self):
        inp = r"A# = 0;"
        exp = CcsRepresentation([ProcessAssignment("A#", NilProcess())], [])
        act = g.parse(inp)
        assert exp == act
    
    def test_weirdly_named_process_prime(self):
        inp = r"A' = 0;"
        exp = CcsRepresentation([ProcessAssignment("A'", NilProcess())], [])
        act = g.parse(inp)
        assert exp == act
    
    def test_weirdly_named_process_dash(self):
        inp = r"A- = 0;"
        exp = CcsRepresentation([ProcessAssignment("A-", NilProcess())], [])
        act = g.parse(inp)
        assert exp == act
    
    def test_weirdly_named_process_qm(self):
        inp = r"A? = 0;"
        exp = CcsRepresentation([ProcessAssignment("A?", NilProcess())], [])
        act = g.parse(inp)
        assert exp == act
    
    def test_weirdly_named_process_circumflex(self):
        inp = r"A^ = 0;"
        exp = CcsRepresentation([ProcessAssignment("A^", NilProcess())], [])
        act = g.parse(inp)
        assert exp == act
    
    def test_weirdly_named_process_underscore(self):
        inp = r"A_ = 0;"
        exp = CcsRepresentation([ProcessAssignment("A_", NilProcess())], [])
        act = g.parse(inp)
        assert exp == act

class Test_Complex_Grammar():
    def test_multi_prefix_alternative_process(self):
        inp = "Testcase = a.'b.One + 'a.b.Two;"
        exp = CcsRepresentation(
            [
                ProcessAssignment(
                    "Testcase",
                    SumProcesses(
                        [
                            PrefixedProcess(
                                Action("a"),
                                PrefixedProcess(
                                    DualAction("b"),
                                    ProcessByName("One"),
                                ),
                            ),
                            PrefixedProcess(
                                DualAction("a"),
                                PrefixedProcess(
                                    Action("b"), ProcessByName("Two")
                                ),
                            ),
                        ]
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        assert exp == act

    def test_multi_alternatives_process(self):
        inp = "Testcase = a.'b.One + 'a.b.Two + a.b.Three + 'a.'b.Four;"
        exp = CcsRepresentation(
            [
                ProcessAssignment(
                    "Testcase",
                    SumProcesses(
                        [
                            PrefixedProcess(
                                Action("a"),
                                PrefixedProcess(
                                    DualAction("b"),
                                    ProcessByName("One"),
                                ),
                            ),
                            PrefixedProcess(
                                DualAction("a"),
                                PrefixedProcess(
                                    Action("b"), ProcessByName("Two")
                                ),
                            ),
                            PrefixedProcess(
                                Action("a"),
                                PrefixedProcess(
                                    Action("b"), ProcessByName("Three")
                                ),
                            ),
                            PrefixedProcess(
                                DualAction("a"),
                                PrefixedProcess(
                                    DualAction("b"),
                                    ProcessByName("Four"),
                                ),
                            ),
                        ]
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        assert exp == act

    def test_alternatives_renaming_process(self):
        inp = "Testcase = (a.'b.One)[x/y] + 'a.b.Two[x/y];"
        exp = CcsRepresentation(
            [
                ProcessAssignment(
                    "Testcase",
                    SumProcesses(
                        [
                            RenamingProcess(
                                PrefixedProcess(
                                    Action("a"),
                                    PrefixedProcess(
                                        DualAction("b"),
                                        ProcessByName("One"),
                                    ),
                                ),
                                [(Action("x"), Action("y"))],
                            ),
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
                        ]
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        assert exp == act

    def test_complex_processA(self):
        inp = "TestcaseComplex1 = A[x/y] + B[x/y];"
        exp = CcsRepresentation(
            [
                ProcessAssignment(
                    "TestcaseComplex1",
                    SumProcesses(
                        [
                            RenamingProcess(
                                ProcessByName("A"), [(Action("x"), Action("y"))]
                            ),
                            RenamingProcess(
                                ProcessByName("B"), [(Action("x"), Action("y"))]
                            ),
                        ]
                    ),
                )
            ],
            [],
        )

        act = g.parse(inp)
        assert exp == act

    def test_complex_processB(self):
        inp = "TestcaseComplex1 = A[x/y] + B[x/y] \\ L;"
        exp = CcsRepresentation(
            [
                ProcessAssignment(
                    "TestcaseComplex1",
                    SumProcesses(
                        [
                            RenamingProcess(
                                ProcessByName("A"), [(Action("x"), Action("y"))]
                            ),
                            HidingProcess(
                                RenamingProcess(
                                    ProcessByName("B"),
                                    [(Action("x"), Action("y"))],
                                ),
                                ActionSetByName("L"),
                            ),
                        ]
                    ),
                )
            ],
            [],
        )

        act = g.parse(inp)
        assert exp == act

    def test_complex_processC(self):
        inp = "TestcaseComplex1 = (A)[x/y] + (B[x/y]) \\ L | 0;"
        exp = CcsRepresentation(
            [
                ProcessAssignment(
                    "TestcaseComplex1",
                    SumProcesses(
                        [
                            RenamingProcess(
                                ProcessByName("A"), [(Action("x"), Action("y"))]
                            ),
                            ParallelProcesses(
                                [
                                    HidingProcess(
                                        RenamingProcess(
                                            ProcessByName("B"),
                                            [(Action("x"), Action("y"))],
                                        ),
                                        ActionSetByName("L"),
                                    ),
                                    NilProcess(),
                                ]
                            ),
                        ]
                    ),
                )
            ],
            [],
        )

        act = g.parse(inp)
        assert exp == act

    # @unittest.skip("too slow.")
    def test_complex_processD(self):
        inp = (
            "Testcase = (((x.y.z.Test) + 'a.'b.0 | a.b.A)[a/b, b/a, x/x]) \\ {a, b, c};"
        )
        exp = CcsRepresentation(
            [
                ProcessAssignment(
                    "Testcase",
                    HidingProcess(
                        RenamingProcess(
                            SumProcesses(
                                [
                                    PrefixedProcess(
                                        Action("x"),
                                        PrefixedProcess(
                                            Action("y"),
                                            PrefixedProcess(
                                                Action("z"), ProcessByName("Test")
                                            ),
                                        ),
                                    ),
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
                                                    Action("b"), ProcessByName("A")
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
                )
            ],
            [],
        )
        act = g.parse(inp)
        assert exp == act

    # @unittest.skip("too slow.")
    def test_complex_processE(self):
        inp = "Testcase = ((a.'b.One)[x/y] + ('a.(b.Two[x/y])) \\ L) | (((x.y.z.Test) + 'a.'b.0 | a.b.A)[a/b, b/a, x/x]) \\ {a, b, c};"
        exp = CcsRepresentation(
            [
                ProcessAssignment(
                    "Testcase",
                    ParallelProcesses(
                        [
                            SumProcesses(
                                [
                                    RenamingProcess(
                                        PrefixedProcess(
                                            Action("a"),
                                            PrefixedProcess(
                                                DualAction("b"),
                                                ProcessByName("One"),
                                            ),
                                        ),
                                        [(Action("x"), Action("y"))],
                                    ),
                                    HidingProcess(
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
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        assert exp == act

class Test_Ccs_Input_Grammar():
    def test_simple_ccs(self):
        inp = """
            A = a.0;
            B = b.0;
            set C = {a, b, c};
        """
        exp = CcsRepresentation(
            [
                ProcessAssignment("A", PrefixedProcess(Action("a"), NilProcess())),
                ProcessAssignment("B", PrefixedProcess(Action("b"), NilProcess())),
            ],
            [
                ActionSetAssignment("C", ActionSet(list(map(Action, ["a", "b", "c"]))))
            ],
        )
        act = g.parse(inp)
        assert exp == act

    def test_basic_buffer(self):
        inputdir = pathlib.Path(__file__).parent.parent

        with open(inputdir / "res" / "basic_buffer.ccs") as f:
            inp = f.read()

        exp = CcsRepresentation([
            ProcessAssignment(
                "Buff3", 
                HidingProcess(
                    ParallelProcesses(
                        list(map(ProcessByName, ["C0", "C1", "C2"]))
                    ),
                    ActionSet(
                        list(map(Action, ["c", "d"]))
                    )
                )
            ),
            ProcessAssignment(
                "C0",
                RenamingProcess(
                    ProcessByName("Cell"),
                    [
                        (Action("c"), Action("b")),
                    ]
                )
            ),
            ProcessAssignment(
                "C1",
                RenamingProcess(
                    ProcessByName("Cell"),
                    [
                        (Action("c"), Action("a")),
                        (Action("d"), Action("b")),
                    ]
                )
            ),
            ProcessAssignment(
                "C2",
                RenamingProcess(
                    ProcessByName("Cell"),
                    [
                        (Action("d"), Action("a")),
                    ]
                )
            ),
            ProcessAssignment(
                "Cell",
                PrefixedProcess(
                    Action("a"),
                    PrefixedProcess(
                        DualAction("b"),
                        ProcessByName("Cell")
                    )
                )
            ),
            ProcessAssignment(
                "Spec",
                PrefixedProcess(
                    Action("a"),
                    ProcessByName("Spec'")
                )
            ),
            ProcessAssignment(
                "Spec'",
                SumProcesses(
                    [
                        PrefixedProcess(
                            DualAction("b"),
                            ProcessByName("Spec")
                        ),
                        PrefixedProcess(
                            Action("a"),
                            ProcessByName("Spec''")
                        )
                    ]
                )
            ),
            ProcessAssignment(
                "Spec''",
                SumProcesses(
                    [
                        PrefixedProcess(
                            DualAction("b"),
                            ProcessByName("Spec'")
                        ),
                        PrefixedProcess(
                            Action("a"),
                            PrefixedProcess(
                                DualAction("b"),
                                ProcessByName("Spec''")
                            )
                        )
                    ]
                )
            ),
        ], [])
        act = g.parse(inp)
        assert exp == act

    def test_dekker(self):
        inputdir = pathlib.Path(__file__).parent.parent

        with open(inputdir / "res" / "dekker.ccs") as f:
            inp = f.read()

        exp = CcsRepresentation(
            [
                ProcessAssignment(
                    "B1f",
                    SumProcesses(
                        [
                            PrefixedProcess(
                                DualAction("b1rf"),
                                ProcessByName("B1f"),
                            ),
                            PrefixedProcess(
                                Action("b1wf"),
                                ProcessByName("B1f"),
                            ),
                            PrefixedProcess(
                                Action("b1wt"),
                                ProcessByName("B1t"),
                            ),
                        ]
                    ),
                ),
                ProcessAssignment(
                    "B1t",
                    SumProcesses(
                        [
                            PrefixedProcess(
                                DualAction("b1rt"),
                                ProcessByName("B1t"),
                            ),
                            PrefixedProcess(
                                Action("b1wt"),
                                ProcessByName("B1t"),
                            ),
                            PrefixedProcess(
                                Action("b1wf"),
                                ProcessByName("B1f"),
                            ),
                        ]
                    ),
                ),
                ProcessAssignment(
                    "B2f",
                    SumProcesses(
                        [
                            PrefixedProcess(
                                DualAction("b2rf"),
                                ProcessByName("B2f"),
                            ),
                            PrefixedProcess(
                                Action("b2wf"),
                                ProcessByName("B2f"),
                            ),
                            PrefixedProcess(
                                Action("b2wt"),
                                ProcessByName("B2t"),
                            ),
                        ]
                    ),
                ),
                ProcessAssignment(
                    "B2t",
                    SumProcesses(
                        [
                            PrefixedProcess(
                                DualAction("b2rt"),
                                ProcessByName("B2t"),
                            ),
                            PrefixedProcess(
                                Action("b2wt"),
                                ProcessByName("B2t"),
                            ),
                            PrefixedProcess(
                                Action("b2wf"),
                                ProcessByName("B2f"),
                            ),
                        ]
                    ),
                ),
                ProcessAssignment(
                    "K1",
                    SumProcesses(
                        [
                            PrefixedProcess(
                                DualAction("kr1"),
                                ProcessByName("K1"),
                            ),
                            PrefixedProcess(
                                Action("kw1"),
                                ProcessByName("K1"),
                            ),
                            PrefixedProcess(
                                Action("kw2"),
                                ProcessByName("K2"),
                            ),
                        ]
                    ),
                ),
                ProcessAssignment(
                    "K2",
                    SumProcesses(
                        [
                            PrefixedProcess(
                                DualAction("kr2"),
                                ProcessByName("K2"),
                            ),
                            PrefixedProcess(
                                Action("kw2"),
                                ProcessByName("K2"),
                            ),
                            PrefixedProcess(
                                Action("kw1"),
                                ProcessByName("K1"),
                            ),
                        ]
                    ),
                ),
                ProcessAssignment(
                    "P1",
                    PrefixedProcess(
                        DualAction("b1wt"),
                        ProcessByName("P11"),
                    ),
                ),
                ProcessAssignment(
                    "P11",
                    SumProcesses(
                        [
                            PrefixedProcess(
                                Action("b2rf"),
                                ProcessByName("P14"),
                            ),
                            PrefixedProcess(
                                Action("b2rt"),
                                ProcessByName("P12"),
                            ),
                        ]
                    ),
                ),
                ProcessAssignment(
                    "P12",
                    SumProcesses(
                        [
                            PrefixedProcess(
                                Action("kr1"),
                                ProcessByName("P11"),
                            ),
                            PrefixedProcess(
                                Action("kr2"),
                                PrefixedProcess(
                                    DualAction("b1wf"),
                                    ProcessByName("P13"),
                                ),
                            ),
                        ]
                    ),
                ),
                ProcessAssignment(
                    "P13",
                    SumProcesses(
                        [
                            PrefixedProcess(
                                Action("kr2"),
                                ProcessByName("P13"),
                            ),
                            PrefixedProcess(
                                Action("kr1"),
                                PrefixedProcess(
                                    DualAction("b1wt"),
                                    ProcessByName("P11"),
                                ),
                            ),
                        ]
                    ),
                ),
                ProcessAssignment(
                    "P14",
                    PrefixedProcess(
                        Action("enter"),
                        PrefixedProcess(
                            Action("exit"),
                            PrefixedProcess(
                                DualAction("kw2"),
                                PrefixedProcess(
                                    DualAction("b1wf"),
                                    ProcessByName("P1"),
                                ),
                            ),
                        ),
                    ),
                ),
                ProcessAssignment(
                    "P2",
                    PrefixedProcess(
                        DualAction("b2wt"),
                        ProcessByName("P21"),
                    ),
                ),
                ProcessAssignment(
                    "P21",
                    SumProcesses(
                        [
                            PrefixedProcess(
                                Action("b1rf"),
                                ProcessByName("P24"),
                            ),
                            PrefixedProcess(
                                Action("b1rt"),
                                ProcessByName("P22"),
                            ),
                        ]
                    ),
                ),
                ProcessAssignment(
                    "P22",
                    SumProcesses(
                        [
                            PrefixedProcess(
                                Action("kr2"),
                                ProcessByName("P21"),
                            ),
                            PrefixedProcess(
                                Action("kr1"),
                                PrefixedProcess(
                                    DualAction("b2wf"),
                                    ProcessByName("P23"),
                                ),
                            ),
                        ]
                    ),
                ),
                ProcessAssignment(
                    "P23",
                    SumProcesses(
                        [
                            PrefixedProcess(
                                Action("kr1"),
                                ProcessByName("P23"),
                            ),
                            PrefixedProcess(
                                Action("kr2"),
                                PrefixedProcess(
                                    DualAction("b2wt"),
                                    ProcessByName("P21"),
                                ),
                            ),
                        ]
                    ),
                ),
                ProcessAssignment(
                    "P24",
                    PrefixedProcess(
                        Action("enter"),
                        PrefixedProcess(
                            Action("exit"),
                            PrefixedProcess(
                                DualAction("kw1"),
                                PrefixedProcess(
                                    DualAction("b2wf"),
                                    ProcessByName("P2"),
                                ),
                            ),
                        ),
                    ),
                ),
                ProcessAssignment(
                    "Pre-Dekker-2",
                    ParallelProcesses(
                        list(map(ProcessByName, [
                            "P1",
                            "P2",
                            "K1",
                            "B1f",
                            "B2f",
                        ]))
                    ),
                ),
                ProcessAssignment(
                    "Dekker-2",
                    HidingProcess(
                        ProcessByName("Pre-Dekker-2"),
                        ActionSetByName("L"),
                    ),
                ),
                ProcessAssignment(
                    "Spec",
                    PrefixedProcess(
                        Action("enter"),
                        PrefixedProcess(
                            Action("exit"),
                            ProcessByName("Spec"),
                        ),
                    ),
                ),
            ],
            [
                ActionSetAssignment(
                    "L",
                    ActionSet(
                        list(map(Action, [
                            "b1rf",
                            "b1rt",
                            "b1wf",
                            "b1wt",
                            "b2rf",
                            "b2rt",
                            "b2wf",
                            "b2wt",
                            "kr1",
                            "kr2",
                            "kw1",
                            "kw2",
                        ]))
                    ),
                )
            ],
        )

        act = g.parse(inp)
        assert exp == act