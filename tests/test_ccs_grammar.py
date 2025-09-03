"""CCS Grammar Tests"""

import unittest
import pyparsing as pp
import pathlib

import ccs2bigraph.ccs.grammar as g
import ccs2bigraph.ccs.representation as r


class Action_Test(unittest.TestCase):
    def test_simple_action(self):
        inp = "a"
        exp = r.Action("a")
        act = g._action.parse_string(inp)[0]  # type: ignore (testing private member)
        self.assertEqual(act, exp, f"{act} != {exp}")

    def test_dual_action(self):
        inp = "'a"
        exp = r.Action("a", r.Action.DUAL_FORM)
        act = g._action.parse_string(inp)[0]  # type: ignore (testing private member)
        self.assertEqual(act, exp, f"{act} != {exp}")

    def test_long_action(self):
        inp = "areallylongactionname"
        exp = r.Action("areallylongactionname")
        act = g._action.parse_string(inp)[0]  # type: ignore (testing private member)
        self.assertEqual(act, exp, f"{act} != {exp}")

    def test_action_with_whitespace(self):
        inp = "  a  "
        exp = r.Action("a")
        act = g._action.parse_string(inp)[0]  # type: ignore (testing private member)
        self.assertEqual(act, exp, f"{act} != {exp}")

    def test_action_with_uppercase(self):
        inp = "aBcDe"
        exp = r.Action("aBcDe")
        act = g._action.parse_string(inp)[0]  # type: ignore (testing private member)
        self.assertEqual(act, exp, f"{act} != {exp}")

    def test_invalid_action_name(self):
        inp = "Invalid"

        with self.assertRaises(pp.exceptions.ParseException):
            g._action.parse_string(inp)  # type: ignore (testing private member)


class Set_Test(unittest.TestCase):
    def test_simple_set(self):
        inp = "{a}"
        exp = r.ActionSet([r.Action("a")])
        act = g._actionset.parse_string(inp)[0]  # type: ignore (testing private member)
        self.assertEqual(act, exp, f"{act} != {exp}")

    def test_long_set(self):
        inp = "{a, b, c, d}"
        exp = r.ActionSet(list(map(r.Action, ["a", "b", "c", "d"])))
        act = g._actionset.parse_string(inp)[0]  # type: ignore (testing private member)
        self.assertEqual(act, exp, f"{act} != {exp}")

    def test_set_assignment(self):
        inp = "set Test = {a, b, c, d};"
        exp = r.ActionSetAssignment(
            "Test", r.ActionSet(list(map(r.Action, ["a", "b", "c", "d"])))
        )
        act = g._actionset_assignment.parse_string(inp)[0]  # type: ignore (testing private member)
        self.assertEqual(act, exp, f"{act} != {exp}")

    def test_weirdly_named_actionset_exlam(self):
        inp = r"set A! = {a};"
        exp = r.Ccs([], [r.ActionSetAssignment("A!", r.ActionSet([r.Action("a")]))])
        act = g.parse(inp)
        self.assertEqual(exp, act)
    
    def test_weirdly_named_actionset_hashpipe(self):
        inp = r"set A# = {a};"
        exp = r.Ccs([], [r.ActionSetAssignment("A#", r.ActionSet([r.Action("a")]))])
        act = g.parse(inp)
        self.assertEqual(exp, act)
    
    def test_weirdly_named_actionset_prime(self):
        inp = r"set A' = {a};"
        exp = r.Ccs([], [r.ActionSetAssignment("A'", r.ActionSet([r.Action("a")]))])
        act = g.parse(inp)
        self.assertEqual(exp, act)
    
    def test_weirdly_named_actionset_dash(self):
        inp = r"set A- = {a};"
        exp = r.Ccs([], [r.ActionSetAssignment("A-", r.ActionSet([r.Action("a")]))])
        act = g.parse(inp)
        self.assertEqual(exp, act)
    
    def test_weirdly_named_actionset_qm(self):
        inp = r"set A? = {a};"
        exp = r.Ccs([], [r.ActionSetAssignment("A?", r.ActionSet([r.Action("a")]))])
        act = g.parse(inp)
        self.assertEqual(exp, act)
    
    def test_weirdly_named_actionset_circumflex(self):
        inp = r"set A^ = {a};"
        exp = r.Ccs([], [r.ActionSetAssignment("A^", r.ActionSet([r.Action("a")]))])
        act = g.parse(inp)
        self.assertEqual(exp, act)
    
    def test_weirdly_named_actionset_underscore(self):
        inp = r"set A_ = {a};"
        exp = r.Ccs([], [r.ActionSetAssignment("A_", r.ActionSet([r.Action("a")]))])
        act = g.parse(inp)
        self.assertEqual(exp, act)


class Simple_Grammar_Test(unittest.TestCase):
    def test_simple_process(self):
        inp = "A = 0;"
        exp = r.Ccs([r.ProcessAssignment("A", r.NilProcess())], [])
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_simple_prefixed_process(self):
        inp = "A = a.0;"
        exp = r.Ccs(
            [
                r.ProcessAssignment(
                    "A", r.PrefixedProcess(r.Action("a"), r.NilProcess())
                )
            ],
            [],
        )
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_dual_prefixed_process(self):
        inp = "A = 'a.0;"
        exp = r.Ccs(
            [
                r.ProcessAssignment(
                    "A",
                    r.PrefixedProcess(
                        r.Action("a", r.Action.DUAL_FORM), r.NilProcess()
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_simple_alternative_process(self):
        inp = "A = a.0 + b.0;"
        exp = r.Ccs(
            [
                r.ProcessAssignment(
                    "A",
                    r.AlternativeProcesses(
                        [
                            r.PrefixedProcess(r.Action("a"), r.NilProcess()),
                            r.PrefixedProcess(r.Action("b"), r.NilProcess()),
                        ]
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_dual_alternative_process(self):
        inp = "A = a.0 + 'b.0;"
        exp = r.Ccs(
            [
                r.ProcessAssignment(
                    "A",
                    r.AlternativeProcesses(
                        [
                            r.PrefixedProcess(r.Action("a"), r.NilProcess()),
                            r.PrefixedProcess(
                                r.Action("b", r.Action.DUAL_FORM), r.NilProcess()
                            ),
                        ]
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_simple_parallel_process(self):
        inp = "A = a.0 | b.0;"
        exp = r.Ccs(
            [
                r.ProcessAssignment(
                    "A",
                    r.ParallelProcesses(
                        [
                            r.PrefixedProcess(r.Action("a"), r.NilProcess()),
                            r.PrefixedProcess(r.Action("b"), r.NilProcess()),
                        ]
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_dual_parallel_process(self):
        inp = "A = 'a.0 | b.0;"
        exp = r.Ccs(
            [
                r.ProcessAssignment(
                    "A",
                    r.ParallelProcesses(
                        [
                            r.PrefixedProcess(
                                r.Action("a", r.Action.DUAL_FORM), r.NilProcess()
                            ),
                            r.PrefixedProcess(r.Action("b"), r.NilProcess()),
                        ]
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_simple_hiding_process(self):
        inp = r"A = a.0 \ {a, b};"
        exp = r.Ccs(
            [
                r.ProcessAssignment(
                    "A",
                    r.PrefixedProcess(
                        r.Action("a"),
                        r.HidingProcess(
                            r.NilProcess(), r.ActionSet([r.Action("a"), r.Action("b")])
                        ),
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_dual_hiding_process(self):
        inp = r"A = ('a.0) \ {a, b};"
        exp = r.Ccs(
            [
                r.ProcessAssignment(
                    "A",
                    r.HidingProcess(
                        r.PrefixedProcess(
                            r.Action("a", r.Action.DUAL_FORM), r.NilProcess()
                        ),
                        r.ActionSet([r.Action("a"), r.Action("b")]),
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_ref_hiding_process(self):
        inp = r"A = ('a.0) \ H;"
        exp = r.Ccs(
            [
                r.ProcessAssignment(
                    "A",
                    r.HidingProcess(
                        r.PrefixedProcess(
                            r.Action("a", r.Action.DUAL_FORM), r.NilProcess()
                        ),
                        r.ActionSetByName("H"),
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_simple_renaming_process(self):
        inp = r"A = a.0[b/a];"
        exp = r.Ccs(
            [
                r.ProcessAssignment(
                    "A",
                    r.PrefixedProcess(
                        r.Action("a"),
                        r.RenamingProcess(
                            r.NilProcess(), [(r.Action("b"), r.Action("a"))]
                        ),
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_long_renaming_process(self):
        inp = r"A = (a.0)[b/a, d/c, f/e];"
        exp = r.Ccs(
            [
                r.ProcessAssignment(
                    "A",
                    r.RenamingProcess(
                        r.PrefixedProcess(r.Action("a"), r.NilProcess()),
                        [
                            (r.Action("b"), r.Action("a")),
                            (r.Action("d"), r.Action("c")),
                            (r.Action("f"), r.Action("e")),
                        ],
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_weirdly_named_process_exlam(self):
        inp = r"A! = 0;"
        exp = r.Ccs([r.ProcessAssignment("A!", r.NilProcess())], [])
        act = g.parse(inp)
        self.assertEqual(exp, act)
    
    def test_weirdly_named_process_hashpipe(self):
        inp = r"A# = 0;"
        exp = r.Ccs([r.ProcessAssignment("A#", r.NilProcess())], [])
        act = g.parse(inp)
        self.assertEqual(exp, act)
    
    def test_weirdly_named_process_prime(self):
        inp = r"A' = 0;"
        exp = r.Ccs([r.ProcessAssignment("A'", r.NilProcess())], [])
        act = g.parse(inp)
        self.assertEqual(exp, act)
    
    def test_weirdly_named_process_dash(self):
        inp = r"A- = 0;"
        exp = r.Ccs([r.ProcessAssignment("A-", r.NilProcess())], [])
        act = g.parse(inp)
        self.assertEqual(exp, act)
    
    def test_weirdly_named_process_qm(self):
        inp = r"A? = 0;"
        exp = r.Ccs([r.ProcessAssignment("A?", r.NilProcess())], [])
        act = g.parse(inp)
        self.assertEqual(exp, act)
    
    def test_weirdly_named_process_circumflex(self):
        inp = r"A^ = 0;"
        exp = r.Ccs([r.ProcessAssignment("A^", r.NilProcess())], [])
        act = g.parse(inp)
        self.assertEqual(exp, act)
    
    def test_weirdly_named_process_underscore(self):
        inp = r"A_ = 0;"
        exp = r.Ccs([r.ProcessAssignment("A_", r.NilProcess())], [])
        act = g.parse(inp)
        self.assertEqual(exp, act)


class Complex_Grammar_Test(unittest.TestCase):
    def test_multi_prefix_alternative_process(self):
        inp = "Testcase = a.'b.One + 'a.b.Two;"
        exp = r.Ccs(
            [
                r.ProcessAssignment(
                    "Testcase",
                    r.AlternativeProcesses(
                        [
                            r.PrefixedProcess(
                                r.Action("a"),
                                r.PrefixedProcess(
                                    r.Action("b", r.Action.DUAL_FORM),
                                    r.ProcessByName("One"),
                                ),
                            ),
                            r.PrefixedProcess(
                                r.Action("a", r.Action.DUAL_FORM),
                                r.PrefixedProcess(
                                    r.Action("b"), r.ProcessByName("Two")
                                ),
                            ),
                        ]
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_multi_alternatives_process(self):
        inp = "Testcase = a.'b.One + 'a.b.Two + a.b.Three + 'a.'b.Four;"
        exp = r.Ccs(
            [
                r.ProcessAssignment(
                    "Testcase",
                    r.AlternativeProcesses(
                        [
                            r.PrefixedProcess(
                                r.Action("a"),
                                r.PrefixedProcess(
                                    r.Action("b", r.Action.DUAL_FORM),
                                    r.ProcessByName("One"),
                                ),
                            ),
                            r.PrefixedProcess(
                                r.Action("a", r.Action.DUAL_FORM),
                                r.PrefixedProcess(
                                    r.Action("b"), r.ProcessByName("Two")
                                ),
                            ),
                            r.PrefixedProcess(
                                r.Action("a"),
                                r.PrefixedProcess(
                                    r.Action("b"), r.ProcessByName("Three")
                                ),
                            ),
                            r.PrefixedProcess(
                                r.Action("a", r.Action.DUAL_FORM),
                                r.PrefixedProcess(
                                    r.Action("b", r.Action.DUAL_FORM),
                                    r.ProcessByName("Four"),
                                ),
                            ),
                        ]
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_alternatives_renaming_process(self):
        inp = "Testcase = (a.'b.One)[x/y] + 'a.b.Two[x/y];"
        exp = r.Ccs(
            [
                r.ProcessAssignment(
                    "Testcase",
                    r.AlternativeProcesses(
                        [
                            r.RenamingProcess(
                                r.PrefixedProcess(
                                    r.Action("a"),
                                    r.PrefixedProcess(
                                        r.Action("b", r.Action.DUAL_FORM),
                                        r.ProcessByName("One"),
                                    ),
                                ),
                                [(r.Action("x"), r.Action("y"))],
                            ),
                            r.PrefixedProcess(
                                r.Action("a", r.Action.DUAL_FORM),
                                r.PrefixedProcess(
                                    r.Action("b"),
                                    r.RenamingProcess(
                                        r.ProcessByName("Two"),
                                        [(r.Action("x"), r.Action("y"))],
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
        self.assertEqual(exp, act)

    def test_complex_processA(self):
        inp = "TestcaseComplex1 = A[x/y] + B[x/y];"
        exp = r.Ccs(
            [
                r.ProcessAssignment(
                    "TestcaseComplex1",
                    r.AlternativeProcesses(
                        [
                            r.RenamingProcess(
                                r.ProcessByName("A"), [(r.Action("x"), r.Action("y"))]
                            ),
                            r.RenamingProcess(
                                r.ProcessByName("B"), [(r.Action("x"), r.Action("y"))]
                            ),
                        ]
                    ),
                )
            ],
            [],
        )

        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_complex_processB(self):
        inp = "TestcaseComplex1 = A[x/y] + B[x/y] \\ L;"
        exp = r.Ccs(
            [
                r.ProcessAssignment(
                    "TestcaseComplex1",
                    r.AlternativeProcesses(
                        [
                            r.RenamingProcess(
                                r.ProcessByName("A"), [(r.Action("x"), r.Action("y"))]
                            ),
                            r.HidingProcess(
                                r.RenamingProcess(
                                    r.ProcessByName("B"),
                                    [(r.Action("x"), r.Action("y"))],
                                ),
                                r.ActionSetByName("L"),
                            ),
                        ]
                    ),
                )
            ],
            [],
        )

        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_complex_processC(self):
        inp = "TestcaseComplex1 = (A)[x/y] + (B[x/y]) \\ L | 0;"
        exp = r.Ccs(
            [
                r.ProcessAssignment(
                    "TestcaseComplex1",
                    r.AlternativeProcesses(
                        [
                            r.RenamingProcess(
                                r.ProcessByName("A"), [(r.Action("x"), r.Action("y"))]
                            ),
                            r.ParallelProcesses(
                                [
                                    r.HidingProcess(
                                        r.RenamingProcess(
                                            r.ProcessByName("B"),
                                            [(r.Action("x"), r.Action("y"))],
                                        ),
                                        r.ActionSetByName("L"),
                                    ),
                                    r.NilProcess(),
                                ]
                            ),
                        ]
                    ),
                )
            ],
            [],
        )

        act = g.parse(inp)
        self.assertEqual(exp, act)

    # @unittest.skip("too slow.")
    def test_complex_processD(self):
        inp = (
            "Testcase = (((x.y.z.Test) + 'a.'b.0 | a.b.A)[a/b, b/a, x/x]) \\ {a, b, c};"
        )
        exp = r.Ccs(
            [
                r.ProcessAssignment(
                    "Testcase",
                    r.HidingProcess(
                        r.RenamingProcess(
                            r.AlternativeProcesses(
                                [
                                    r.PrefixedProcess(
                                        r.Action("x"),
                                        r.PrefixedProcess(
                                            r.Action("y"),
                                            r.PrefixedProcess(
                                                r.Action("z"), r.ProcessByName("Test")
                                            ),
                                        ),
                                    ),
                                    r.ParallelProcesses(
                                        [
                                            r.PrefixedProcess(
                                                r.Action("a", r.Action.DUAL_FORM),
                                                r.PrefixedProcess(
                                                    r.Action("b", r.Action.DUAL_FORM),
                                                    r.NilProcess(),
                                                ),
                                            ),
                                            r.PrefixedProcess(
                                                r.Action("a"),
                                                r.PrefixedProcess(
                                                    r.Action("b"), r.ProcessByName("A")
                                                ),
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            [
                                (r.Action("a"), r.Action("b")),
                                (r.Action("b"), r.Action("a")),
                                (r.Action("x"), r.Action("x")),
                            ],
                        ),
                        r.ActionSet(list(map(r.Action, ["a", "b", "c"]))),
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        self.assertEqual(exp, act)

    # @unittest.skip("too slow.")
    def test_complex_processE(self):
        inp = "Testcase = ((a.'b.One)[x/y] + ('a.(b.Two[x/y])) \\ L) | (((x.y.z.Test) + 'a.'b.0 | a.b.A)[a/b, b/a, x/x]) \\ {a, b, c};"
        exp = r.Ccs(
            [
                r.ProcessAssignment(
                    "Testcase",
                    r.ParallelProcesses(
                        [
                            r.AlternativeProcesses(
                                [
                                    r.RenamingProcess(
                                        r.PrefixedProcess(
                                            r.Action("a"),
                                            r.PrefixedProcess(
                                                r.Action("b", r.Action.DUAL_FORM),
                                                r.ProcessByName("One"),
                                            ),
                                        ),
                                        [(r.Action("x"), r.Action("y"))],
                                    ),
                                    r.HidingProcess(
                                        r.PrefixedProcess(
                                            r.Action("a", r.Action.DUAL_FORM),
                                            r.PrefixedProcess(
                                                r.Action("b"),
                                                r.RenamingProcess(
                                                    r.ProcessByName("Two"),
                                                    [(r.Action("x"), r.Action("y"))],
                                                ),
                                            ),
                                        ),
                                        r.ActionSetByName("L"),
                                    ),
                                ]
                            ),
                            r.HidingProcess(
                                r.RenamingProcess(
                                    r.AlternativeProcesses(
                                        [
                                            r.PrefixedProcess(
                                                r.Action("x"),
                                                r.PrefixedProcess(
                                                    r.Action("y"),
                                                    r.PrefixedProcess(
                                                        r.Action("z"),
                                                        r.ProcessByName("Test"),
                                                    ),
                                                ),
                                            ),
                                            r.ParallelProcesses(
                                                [
                                                    r.PrefixedProcess(
                                                        r.Action(
                                                            "a", r.Action.DUAL_FORM
                                                        ),
                                                        r.PrefixedProcess(
                                                            r.Action(
                                                                "b", r.Action.DUAL_FORM
                                                            ),
                                                            r.NilProcess(),
                                                        ),
                                                    ),
                                                    r.PrefixedProcess(
                                                        r.Action("a"),
                                                        r.PrefixedProcess(
                                                            r.Action("b"),
                                                            r.ProcessByName("A"),
                                                        ),
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                    [
                                        (r.Action("a"), r.Action("b")),
                                        (r.Action("b"), r.Action("a")),
                                        (r.Action("x"), r.Action("x")),
                                    ],
                                ),
                                r.ActionSet(list(map(r.Action, ["a", "b", "c"]))),
                            ),
                        ]
                    ),
                )
            ],
            [],
        )
        act = g.parse(inp)
        self.assertEqual(exp, act)

class Ccs_Input_Grammar_Test(unittest.TestCase):
    def test_simple_ccs(self):
        inp = """
            A = a.0;
            B = b.0;
            set C = {a, b, c};
        """
        exp = r.Ccs(
            [
                r.ProcessAssignment("A", r.PrefixedProcess(r.Action("a"), r.NilProcess())),
                r.ProcessAssignment("B", r.PrefixedProcess(r.Action("b"), r.NilProcess())),
            ],
            [
                r.ActionSetAssignment("C", r.ActionSet(list(map(r.Action, ["a", "b", "c"]))))
            ],
        )
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_basic_buffer(self):
        inputdir = pathlib.Path(__file__).parent

        with open(inputdir / "res" / "basic_buffer.ccs") as f:
            inp = f.read()

        exp = r.Ccs([
            r.ProcessAssignment(
                "Buff3", 
                r.HidingProcess(
                    r.ParallelProcesses(
                        list(map(r.ProcessByName, ["C0", "C1", "C2"]))
                    ),
                    r.ActionSet(
                        list(map(r.Action, ["c", "d"]))
                    )
                )
            ),
            r.ProcessAssignment(
                "C0",
                r.RenamingProcess(
                    r.ProcessByName("Cell"),
                    [
                        (r.Action("c"), r.Action("b")),
                    ]
                )
            ),
            r.ProcessAssignment(
                "C1",
                r.RenamingProcess(
                    r.ProcessByName("Cell"),
                    [
                        (r.Action("c"), r.Action("a")),
                        (r.Action("d"), r.Action("b")),
                    ]
                )
            ),
            r.ProcessAssignment(
                "C2",
                r.RenamingProcess(
                    r.ProcessByName("Cell"),
                    [
                        (r.Action("d"), r.Action("a")),
                    ]
                )
            ),
            r.ProcessAssignment(
                "Cell",
                r.PrefixedProcess(
                    r.Action("a"),
                    r.PrefixedProcess(
                        r.Action("b", r.Action.DUAL_FORM),
                        r.ProcessByName("Cell")
                    )
                )
            ),
            r.ProcessAssignment(
                "Spec",
                r.PrefixedProcess(
                    r.Action("a"),
                    r.ProcessByName("Spec'")
                )
            ),
            r.ProcessAssignment(
                "Spec'",
                r.AlternativeProcesses(
                    [
                        r.PrefixedProcess(
                            r.Action("b", r.Action.DUAL_FORM),
                            r.ProcessByName("Spec")
                        ),
                        r.PrefixedProcess(
                            r.Action("a"),
                            r.ProcessByName("Spec''")
                        )
                    ]
                )
            ),
            r.ProcessAssignment(
                "Spec''",
                r.AlternativeProcesses(
                    [
                        r.PrefixedProcess(
                            r.Action("b", r.Action.DUAL_FORM),
                            r.ProcessByName("Spec'")
                        ),
                        r.PrefixedProcess(
                            r.Action("a"),
                            r.PrefixedProcess(
                                r.Action("b", r.Action.DUAL_FORM),
                                r.ProcessByName("Spec''")
                            )
                        )
                    ]
                )
            ),
        ], [])
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_dekker(self):
        inputdir = pathlib.Path(__file__).parent

        with open(inputdir / "res" / "dekker.ccs") as f:
            inp = f.read()

        exp = r.Ccs(
            [
                r.ProcessAssignment(
                    "B1f",
                    r.AlternativeProcesses(
                        [
                            r.PrefixedProcess(
                                r.Action("b1rf", r.Action.DUAL_FORM),
                                r.ProcessByName("B1f"),
                            ),
                            r.PrefixedProcess(
                                r.Action("b1wf"),
                                r.ProcessByName("B1f"),
                            ),
                            r.PrefixedProcess(
                                r.Action("b1wt"),
                                r.ProcessByName("B1t"),
                            ),
                        ]
                    ),
                ),
                r.ProcessAssignment(
                    "B1t",
                    r.AlternativeProcesses(
                        [
                            r.PrefixedProcess(
                                r.Action("b1rt", r.Action.DUAL_FORM),
                                r.ProcessByName("B1t"),
                            ),
                            r.PrefixedProcess(
                                r.Action("b1wt"),
                                r.ProcessByName("B1t"),
                            ),
                            r.PrefixedProcess(
                                r.Action("b1wf"),
                                r.ProcessByName("B1f"),
                            ),
                        ]
                    ),
                ),
                r.ProcessAssignment(
                    "B2f",
                    r.AlternativeProcesses(
                        [
                            r.PrefixedProcess(
                                r.Action("b2rf", r.Action.DUAL_FORM),
                                r.ProcessByName("B2f"),
                            ),
                            r.PrefixedProcess(
                                r.Action("b2wf"),
                                r.ProcessByName("B2f"),
                            ),
                            r.PrefixedProcess(
                                r.Action("b2wt"),
                                r.ProcessByName("B2t"),
                            ),
                        ]
                    ),
                ),
                r.ProcessAssignment(
                    "B2t",
                    r.AlternativeProcesses(
                        [
                            r.PrefixedProcess(
                                r.Action("b2rt", r.Action.DUAL_FORM),
                                r.ProcessByName("B2t"),
                            ),
                            r.PrefixedProcess(
                                r.Action("b2wt"),
                                r.ProcessByName("B2t"),
                            ),
                            r.PrefixedProcess(
                                r.Action("b2wf"),
                                r.ProcessByName("B2f"),
                            ),
                        ]
                    ),
                ),
                r.ProcessAssignment(
                    "K1",
                    r.AlternativeProcesses(
                        [
                            r.PrefixedProcess(
                                r.Action("kr1", r.Action.DUAL_FORM),
                                r.ProcessByName("K1"),
                            ),
                            r.PrefixedProcess(
                                r.Action("kw1"),
                                r.ProcessByName("K1"),
                            ),
                            r.PrefixedProcess(
                                r.Action("kw2"),
                                r.ProcessByName("K2"),
                            ),
                        ]
                    ),
                ),
                r.ProcessAssignment(
                    "K2",
                    r.AlternativeProcesses(
                        [
                            r.PrefixedProcess(
                                r.Action("kr2", r.Action.DUAL_FORM),
                                r.ProcessByName("K2"),
                            ),
                            r.PrefixedProcess(
                                r.Action("kw2"),
                                r.ProcessByName("K2"),
                            ),
                            r.PrefixedProcess(
                                r.Action("kw1"),
                                r.ProcessByName("K1"),
                            ),
                        ]
                    ),
                ),
                r.ProcessAssignment(
                    "P1",
                    r.PrefixedProcess(
                        r.Action("b1wt", r.Action.DUAL_FORM),
                        r.ProcessByName("P11"),
                    ),
                ),
                r.ProcessAssignment(
                    "P11",
                    r.AlternativeProcesses(
                        [
                            r.PrefixedProcess(
                                r.Action("b2rf"),
                                r.ProcessByName("P14"),
                            ),
                            r.PrefixedProcess(
                                r.Action("b2rt"),
                                r.ProcessByName("P12"),
                            ),
                        ]
                    ),
                ),
                r.ProcessAssignment(
                    "P12",
                    r.AlternativeProcesses(
                        [
                            r.PrefixedProcess(
                                r.Action("kr1"),
                                r.ProcessByName("P11"),
                            ),
                            r.PrefixedProcess(
                                r.Action("kr2"),
                                r.PrefixedProcess(
                                    r.Action("b1wf", r.Action.DUAL_FORM),
                                    r.ProcessByName("P13"),
                                ),
                            ),
                        ]
                    ),
                ),
                r.ProcessAssignment(
                    "P13",
                    r.AlternativeProcesses(
                        [
                            r.PrefixedProcess(
                                r.Action("kr2"),
                                r.ProcessByName("P13"),
                            ),
                            r.PrefixedProcess(
                                r.Action("kr1"),
                                r.PrefixedProcess(
                                    r.Action("b1wt", r.Action.DUAL_FORM),
                                    r.ProcessByName("P11"),
                                ),
                            ),
                        ]
                    ),
                ),
                r.ProcessAssignment(
                    "P14",
                    r.PrefixedProcess(
                        r.Action("enter"),
                        r.PrefixedProcess(
                            r.Action("exit"),
                            r.PrefixedProcess(
                                r.Action("kw2", r.Action.DUAL_FORM),
                                r.PrefixedProcess(
                                    r.Action("b1wf", r.Action.DUAL_FORM),
                                    r.ProcessByName("P1"),
                                ),
                            ),
                        ),
                    ),
                ),
                r.ProcessAssignment(
                    "P2",
                    r.PrefixedProcess(
                        r.Action("b2wt", r.Action.DUAL_FORM),
                        r.ProcessByName("P21"),
                    ),
                ),
                r.ProcessAssignment(
                    "P21",
                    r.AlternativeProcesses(
                        [
                            r.PrefixedProcess(
                                r.Action("b1rf"),
                                r.ProcessByName("P24"),
                            ),
                            r.PrefixedProcess(
                                r.Action("b1rt"),
                                r.ProcessByName("P22"),
                            ),
                        ]
                    ),
                ),
                r.ProcessAssignment(
                    "P22",
                    r.AlternativeProcesses(
                        [
                            r.PrefixedProcess(
                                r.Action("kr2"),
                                r.ProcessByName("P21"),
                            ),
                            r.PrefixedProcess(
                                r.Action("kr1"),
                                r.PrefixedProcess(
                                    r.Action("b2wf", r.Action.DUAL_FORM),
                                    r.ProcessByName("P23"),
                                ),
                            ),
                        ]
                    ),
                ),
                r.ProcessAssignment(
                    "P23",
                    r.AlternativeProcesses(
                        [
                            r.PrefixedProcess(
                                r.Action("kr1"),
                                r.ProcessByName("P23"),
                            ),
                            r.PrefixedProcess(
                                r.Action("kr2"),
                                r.PrefixedProcess(
                                    r.Action("b2wt", r.Action.DUAL_FORM),
                                    r.ProcessByName("P21"),
                                ),
                            ),
                        ]
                    ),
                ),
                r.ProcessAssignment(
                    "P24",
                    r.PrefixedProcess(
                        r.Action("enter"),
                        r.PrefixedProcess(
                            r.Action("exit"),
                            r.PrefixedProcess(
                                r.Action("kw1", r.Action.DUAL_FORM),
                                r.PrefixedProcess(
                                    r.Action("b2wf", r.Action.DUAL_FORM),
                                    r.ProcessByName("P2"),
                                ),
                            ),
                        ),
                    ),
                ),
                r.ProcessAssignment(
                    "Pre-Dekker-2",
                    r.ParallelProcesses(
                        list(map(r.ProcessByName, [
                            "P1",
                            "P2",
                            "K1",
                            "B1f",
                            "B2f",
                        ]))
                    ),
                ),
                r.ProcessAssignment(
                    "Dekker-2",
                    r.HidingProcess(
                        r.ProcessByName("Pre-Dekker-2"),
                        r.ActionSetByName("L"),
                    ),
                ),
                r.ProcessAssignment(
                    "Spec",
                    r.PrefixedProcess(
                        r.Action("enter"),
                        r.PrefixedProcess(
                            r.Action("exit"),
                            r.ProcessByName("Spec"),
                        ),
                    ),
                ),
            ],
            [
                r.ActionSetAssignment(
                    "L",
                    r.ActionSet(
                        list(map(r.Action, [
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
        self.assertEqual(exp, act)

if __name__ == "__main__":
    unittest.main()
