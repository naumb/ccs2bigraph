"""CCS Grammar Tests"""

import unittest
import pyparsing as pp

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


if __name__ == "__main__":
    unittest.main()
