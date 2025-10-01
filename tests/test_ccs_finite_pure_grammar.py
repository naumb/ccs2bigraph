"""CCS Finite Pure Grammar Tests"""

import pyparsing as pp

import pytest

import ccs2bigraph.ccs.finite_pure_grammar as g
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

        with pytest.raises(pp.ParseException):
            g._action.parse_string(inp)  # type: ignore (testing private member)

class Test_Simple_Finite_Pure_Grammar():
    def test_nil_process(self):
        inp = "0"
        exp = NilProcess()
        assert g.parse(inp) == exp

    def test_invalid_nil_alternative(self):
        inp = "0 + 0"
        with pytest.raises(pp.ParseException):
            g.parse(inp)

    def test_prefix(self):
        inp = "a.0"
        exp = PrefixedProcess(Action("a"), NilProcess())
        assert g.parse(inp) == exp

    def test_multi_prefix(self):
        inp = "a.b.c.0"
        exp = PrefixedProcess(
            Action("a"), 
            PrefixedProcess(
                Action("b"),
                PrefixedProcess(
                    Action("c"),
                    NilProcess(),
                )
            )    
        )
        assert g.parse(inp) == exp

    def test_multi_dual_prefix(self):
        inp = "'a.b.'c.0"
        exp = PrefixedProcess(
            DualAction("a"), 
            PrefixedProcess(
                Action("b"),
                PrefixedProcess(
                    DualAction("c"),
                    NilProcess(),
                )
            )    
        )
        assert g.parse(inp) == exp

    def test_parallel_nil(self):
        inp = "0 | 0"
        exp = ParallelProcesses(
            [NilProcess(), NilProcess()]
        )
        assert g.parse(inp) == exp

    def test_multi_parallel_nil(self):
        inp = "0 | 0 | 0 | 0"
        exp = ParallelProcesses(
            [NilProcess(), NilProcess(), NilProcess(), NilProcess()]
        )
        assert g.parse(inp) == exp

    def test_hiding_process(self):
        inp = "/x(0)"
        exp = HidingProcess(
            NilProcess(),
            ActionSet([Action("x")])
        )
        assert g.parse(inp) == exp

    def test_hiding_process_2(self):
        inp = "/x 0"
        exp = HidingProcess(
            NilProcess(),
            ActionSet([Action("x")])
        )
        assert g.parse(inp) == exp

    def test_invalid_hiding_process(self):
        inp = "/x0" # Invalid, since x0 is interpreted as an action an therefore 0 is not interpreted as the process.
        with pytest.raises(pp.ParseException):
            g.parse(inp)
    
    @pytest.mark.skip()
    def test_parallel_prefix(self):
        inp = "a.0 | b.0"
        exp = ParallelProcesses(
            [
                PrefixedProcess(
                    Action("a"),
                    NilProcess(),
                ),
                PrefixedProcess(
                    Action("b"),
                    NilProcess()
                )
            ]
        )
        assert g.parse(inp) == exp

    @pytest.mark.skip()
    def test_complex_process(self):
        inp = "( (a.0) | ('a.0) | (b.0 + c.0) | (/d('b.0 + d.0)))"
        exp = ParallelProcesses(
            [
                PrefixedProcess(
                    Action("a"),
                    NilProcess(),
                ),
                PrefixedProcess(
                    DualAction("a"),
                    NilProcess(),
                ),
                SumProcesses(
                    [
                        PrefixedProcess(
                            Action("b"),
                            NilProcess(),
                        ),
                        PrefixedProcess(
                            Action("c"),
                            NilProcess(),
                        ),
                    ]
                ),
                HidingProcess(
                    SumProcesses(
                        [
                            PrefixedProcess(
                                DualAction("b"),
                                NilProcess(),
                            ),
                            PrefixedProcess(
                                Action("d"),
                                NilProcess()
                            )
                        ]
                    ),
                    ActionSet(
                        [
                            Action("d")
                        ]
                    )
                ),
            ]
        )
        assert g.parse(inp) == exp