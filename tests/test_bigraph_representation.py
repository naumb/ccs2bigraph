"""Bigraph Representation Tests"""

import unittest

from ccs2bigraph.bigraph.representation import *

class Control_Tests(unittest.TestCase):
    def test_simple_control(self):
        inp = ControlDefinition(Control("A", 0))
        exp = "ctrl A = 0;"
        act = str(inp)
        self.assertEqual(exp, act)

    def test_arity_control(self):
        inp = ControlDefinition(Control("A", 42))
        exp = "ctrl A = 42;"
        act = str(inp)
        self.assertEqual(exp, act)

    def test_atomic_control(self):
        inp = ControlDefinition(AtomicControl("A", 0))
        exp = "atomic ctrl A = 0;"
        act = str(inp)
        self.assertEqual(exp, act)

    def test_atomic_arity_control(self):
        inp = ControlDefinition(AtomicControl("A", 42))
        exp = "atomic ctrl A = 42;"
        act = str(inp)
        self.assertEqual(exp, act)

    def test_control_by_name(self):
        inp = ControlByName("A")
        exp = "A"
        act = str(inp)
        self.assertEqual(exp, act)

class Link_Tests(unittest.TestCase):
    def test_simple_link(self):
        inp = Link("a")
        exp = "a"
        act = str(inp)
        self.assertEqual(exp, act)

class Bigraph_Tests(unittest.TestCase):
    def test_one_bigraph(self):
        inp = OneBigraph()
        exp = "1"
        act = str(inp)
        self.assertEqual(exp, act)

    def test_id_bigraph(self):
        inp = IdBigraph()
        exp = "id"
        act = str(inp)
        self.assertEqual(exp, act)

    def test_control_bigraph(self):
        inp = ControlBigraph(ControlByName('A'), [Link('a')])
        exp = r"A{a}"
        act = str(inp)
        self.assertEqual(exp, act)

    def test_nesting_bigraph(self):
        inp = NestingBigraph(
            ControlBigraph(
                ControlByName("C"),
                [Link("a"), Link("b")]
            ),
            IdBigraph()
        )
        exp = r"(C{a,b}.id)"
        act = str(inp)
        self.assertEqual(exp, act)

    def test_merging_bigraph(self):
        inp = MergedBigraphs([
            ControlBigraph(
                ControlByName("A"),
                []
            ),
            ControlBigraph(
                ControlByName("B"),
                []
            ),
        ])
        exp = r"(A | B)"
        act = str(inp)
        self.assertEqual(exp, act)

    def test_multi_merging_bigraph(self):
        inp = MergedBigraphs([
            ControlBigraph(
                ControlByName("A"),
                []
            ),
            ControlBigraph(
                ControlByName("B"),
                []
            ),
            ControlBigraph(
                ControlByName("C"),
                []
            ),
            ControlBigraph(
                ControlByName("D"),
                []
            ),
        ])
        exp = r"(A | B | C | D)"
        act = str(inp)
        self.assertEqual(exp, act)

    def test_merging_link_bigraph(self):
        inp = MergedBigraphs([
            ControlBigraph(
                ControlByName("A"),
                [Link("a")]
            ),
            ControlBigraph(
                ControlByName("B"),
                [Link("b")]
            ),
        ])
        exp = r"(A{a} | B{b})"
        act = str(inp)
        self.assertEqual(exp, act)
    
    def test_multi_merging_link_bigraph(self):
        inp = MergedBigraphs([
            ControlBigraph(
                ControlByName("A"),
                list(map(Link, ["b", "c", "d"]))
            ),
            ControlBigraph(
                ControlByName("B"),
                list(map(Link, ["a", "c", "d"]))
            ),
            ControlBigraph(
                ControlByName("C"),
                list(map(Link, ["a", "b", "d"]))
            ),
            ControlBigraph(
                ControlByName("D"),
                list(map(Link, ["a", "b", "c"]))
            ),
        ])
        exp = r"(A{b,c,d} | B{a,c,d} | C{a,b,d} | D{a,b,c})"
        act = str(inp)
        self.assertEqual(exp, act)