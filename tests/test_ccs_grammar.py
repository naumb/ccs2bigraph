"""CCS Grammar Tests"""

import unittest
import pyparsing as pp

import ccs2bigraph.ccs.grammar as g
import ccs2bigraph.ccs.evaluation as e

class Action_Test(unittest.TestCase):
    def test_simple_action(self):
        inp = 'a'

        exp = e.Action('a')
        print(f"Expected: {str(exp)}")

        act = g._action.parse_string(inp)[0] # type: ignore (testing private member)
        print(f"Actual: {str(act)}")

        self.assertEqual(act, exp, f"{act} != {exp}")


    def test_dual_action(self):
        inp = "'a"
        exp = e.Action('a', e.Action.DUAL_FORM)
        act = g._action.parse_string(inp)[0] # type: ignore (testing private member)
        
        self.assertEqual(act, exp, f"{act} != {exp}")


    def test_long_action(self):
        inp = 'areallylongactionname'
        exp = e.Action('areallylongactionname')
        act = g._action.parse_string(inp)[0] # type: ignore (testing private member)
        self.assertEqual(act, exp, f"{act} != {exp}")


    def test_action_with_whitespace(self):
        inp = '  a  '
        exp = e.Action('a')
        act = g._action.parse_string(inp)[0] # type: ignore (testing private member)
        self.assertEqual(act, exp, f"{act} != {exp}")


    def test_action_with_uppercase(self):
        inp = 'aBcDe'
        exp = e.Action('aBcDe')
        act = g._action.parse_string(inp)[0] # type: ignore (testing private member)
        self.assertEqual(act, exp, f"{act} != {exp}")

    
    def test_invalid_action_name(self):
        inp = 'Invalid'

        with self.assertRaises(pp.exceptions.ParseException):
            g._action.parse_string(inp) # type: ignore (testing private member)

class Set_Test(unittest.TestCase):
    def test_simple_set(self):
        inp = "{a}"
        exp = e.ActionSet([e.Action("a")])
        act = g._actionset.parse_string(inp)[0] # type: ignore (testing private member)
        self.assertEqual(act, exp, f"{act} != {exp}")

    def test_long_set(self):
        inp = "{a, b, c, d}"
        exp = e.ActionSet(list(map(e.Action, ["a", "b", "c", "d"])))
        act = g._actionset.parse_string(inp)[0] # type: ignore (testing private member)
        self.assertEqual(act, exp, f"{act} != {exp}")

    def test_named_set(self):
        inp = "set Test = {a, b, c, d};"
        exp = e.NamedActionSet("Test", e.ActionSet(list(map(e.Action, ["a", "b", "c", "d"]))))
        act = g._actionset_assignment.parse_string(inp)[0] # type: ignore (testing private member)
        self.assertEqual(act, exp, f"{act} != {exp}")


class Simple_Grammar_Test(unittest.TestCase):
    def test_simple_process(self):
        inp = "A = 0;"
        exp = e.ProcessAssignment(e.NamedProcess("A"), e.NilProcess())
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_simple_prefixed_process(self):
        inp = "A = a.0;"
        exp = e.ProcessAssignment(e.NamedProcess("A"), e.PrefixedProcess(e.Action("a"), e.NilProcess()))
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_dual_prefixed_process(self):
        inp = "A = 'a.0;"
        exp = e.ProcessAssignment(e.NamedProcess("A"), e.PrefixedProcess(e.Action("a", e.Action.DUAL_FORM), e.NilProcess()))
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_simple_alternative_process(self):
        inp = "A = a.0 + b.0;"
        exp = e.ProcessAssignment(e.NamedProcess("A"), e.AlternativeProcesses([
            e.PrefixedProcess(e.Action("a"), e.NilProcess()),
            e.PrefixedProcess(e.Action("b"), e.NilProcess())
        ]))
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_dual_alternative_process(self):
        inp = "A = a.0 + 'b.0;"
        exp = e.ProcessAssignment(e.NamedProcess("A"), e.AlternativeProcesses([
            e.PrefixedProcess(e.Action("a"), e.NilProcess()),
            e.PrefixedProcess(e.Action("b", e.Action.DUAL_FORM), e.NilProcess())
        ]))
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_simple_parallel_process(self):
        inp = "A = a.0 | b.0;"
        exp = e.ProcessAssignment(e.NamedProcess("A"), e.ParallelProcesses([
            e.PrefixedProcess(e.Action("a"), e.NilProcess()),
            e.PrefixedProcess(e.Action("b"), e.NilProcess())
        ]))
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_dual_parallel_process(self):
        inp = "A = 'a.0 | b.0;"
        exp = e.ProcessAssignment(e.NamedProcess("A"), e.ParallelProcesses([
            e.PrefixedProcess(e.Action("a", e.Action.DUAL_FORM), e.NilProcess()),
            e.PrefixedProcess(e.Action("b"), e.NilProcess())
        ]))
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_simple_hiding_process(self):
        inp = r"A = a.0 \ {a, b};"
        exp = e.ProcessAssignment(e.NamedProcess("A"), e.PrefixedProcess(e.Action("a"), e.HidingProcess(e.NilProcess(),
            e.ActionSet([
                e.Action("a"), e.Action("b") 
            ])
        )))
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_dual_hiding_process(self):
        inp = r"A = ('a.0) \ {a, b};"
        exp = e.ProcessAssignment(e.NamedProcess("A"), e.HidingProcess(
            e.PrefixedProcess(e.Action("a", e.Action.DUAL_FORM), e.NilProcess()),
            e.ActionSet([
                e.Action("a"), e.Action("b") 
            ])
        ))
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_ref_hiding_process(self):
        inp = r"A = ('a.0) \ H;"
        exp = e.ProcessAssignment(e.NamedProcess("A"), e.HidingProcess(
            e.PrefixedProcess(e.Action("a", e.Action.DUAL_FORM), e.NilProcess()),
            "H"
        ))
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_simple_renaming_process(self):
        inp = r"A = a.0[b/a];"
        exp = e.ProcessAssignment(e.NamedProcess("A"), 
            e.PrefixedProcess(
                e.Action("a"), e.RenamingProcess(e.NilProcess(),
                    [(e.Action("b"), e.Action("a"))])
            )
        )
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_long_renaming_process(self):
        inp = r"A = (a.0)[b/a, d/c, f/e];"
        exp = e.ProcessAssignment(e.NamedProcess("A"), e.RenamingProcess(
            e.PrefixedProcess(e.Action("a"), e.NilProcess()),
            [
                (e.Action("b"), e.Action("a")),
                (e.Action("d"), e.Action("c")),
                (e.Action("f"), e.Action("e")),
            ]
        ))
        act = g.parse(inp)
        self.assertEqual(exp, act)


class Complex_Grammar_Test(unittest.TestCase):
    def test_multi_prefix_alternative_process(self):
        inp = "Testcase = a.'b.One + 'a.b.Two;"
        exp = e.ProcessAssignment(
            e.NamedProcess("Testcase"), 
            e.AlternativeProcesses([
                e.PrefixedProcess(e.Action("a"), e.PrefixedProcess(e.Action("b", e.Action.DUAL_FORM), e.NamedProcess("One"))),
                e.PrefixedProcess(e.Action("a", e.Action.DUAL_FORM), e.PrefixedProcess(e.Action("b"), e.NamedProcess("Two")))
            ])
        )
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_multi_alternatives_process(self):
        inp = "Testcase = a.'b.One + 'a.b.Two + a.b.Three + 'a.'b.Four;"
        exp = e.ProcessAssignment(
            e.NamedProcess("Testcase"), 
            e.AlternativeProcesses([
                e.PrefixedProcess(e.Action("a"), e.PrefixedProcess(e.Action("b", e.Action.DUAL_FORM), e.NamedProcess("One"))),
                e.PrefixedProcess(e.Action("a", e.Action.DUAL_FORM), e.PrefixedProcess(e.Action("b"), e.NamedProcess("Two"))),
                e.PrefixedProcess(e.Action("a"), e.PrefixedProcess(e.Action("b"), e.NamedProcess("Three"))),
                e.PrefixedProcess(e.Action("a", e.Action.DUAL_FORM), e.PrefixedProcess(e.Action("b", e.Action.DUAL_FORM), e.NamedProcess("Four"))),
            ])
        )
        act = g.parse(inp)
        self.assertEqual(exp, act)

    def test_alternatives_renaming_process(self):
        inp = "Testcase = (a.'b.One)[x/y] + 'a.b.Two[x/y];"
        exp = e.ProcessAssignment(
            e.NamedProcess("Testcase"), 
            e.AlternativeProcesses([
                e.RenamingProcess(
                    e.PrefixedProcess(e.Action("a"), 
                        e.PrefixedProcess(e.Action("b", e.Action.DUAL_FORM), 
                            e.NamedProcess("One"))),
                    [(e.Action("x"), e.Action("y"))]),
                e.PrefixedProcess(e.Action("a", e.Action.DUAL_FORM), 
                    e.PrefixedProcess(e.Action("b"), 
                        e.RenamingProcess(e.NamedProcess("Two"), 
                        [(e.Action("x"), e.Action("y"))])))
            ]))
        act = g.parse(inp) 
        print(act)
        self.assertEqual(exp, act)

    def test_complex_process(self):
        inp = "Testcase = (a.'b.One)[x/y] + ('a.(b.Two[x/y])) \ L | (((x.y.z.Test) + 'a.'b.0 | a.b.A)[a/b, b/a, x/x]) \ {a, b, c};"
        exp = e.ProcessAssignment(
            e.NamedProcess("Testcase"),
            e.ParallelProcesses([
                e.AlternativeProcesses([
                    e.RenamingProcess(
                        e.PrefixedProcess(
                            e.Action("a"),
                            e.PrefixedProcess(
                                e.Action("b", e.Action.DUAL_FORM),
                                e.NamedProcess("One")
                            )
                        ),
                        [(e.Action(x), e.Action(y))]
                    ),
                    e.HidingProcess(
                        e.PrefixedProcess(
                            e.Action("a", e.Action.DUAL_FORM),
                            e.PrefixedProcess(
                                e.Action("b"),
                                e.RenamingProcess(
                                    e.NamedProcess("Two"),
                                    [(e.Action("x"), e.Action("y"))]
                                )
                            )
                        ),
                        "L"
                    )
                ]),
                # Still not done, second half is still missing.
                # Hiding, Renaming, Parallel, Alternative.
            ])
        )
        act = g.parse(inp) 
        print(act)
        self.assertEqual(exp, act)

if __name__ == '__main__':
    unittest.main()