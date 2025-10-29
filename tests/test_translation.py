"""
CCS to Bigraph Translation Tests
"""

import pytest

from ccs2bigraph.ccs.representation import *
from ccs2bigraph.bigraph.representation import *
from ccs2bigraph.translation import FiniteCcsTranslator

from textwrap import dedent


class Test_Ccs_Controls():
    CCS_CONTROLS_RESULT = dedent("""\
        ctrl Ccs = 0;
        ctrl Execute = 0;
        ctrl Process = 1;
        atomic ctrl Call = 1;
        ctrl Alt = 0;
        ctrl Send = 1;
        ctrl Get = 1;
        atomic ctrl Nil = 0;
    """)

    def test_controls(self):
        inp = FiniteCcsTranslator.CCS_CONTROLS
        exp = self.CCS_CONTROLS_RESULT
        act = "\n".join(map(str, inp)) + "\n"
        assert exp == act

class Test_Ccs_ReactionRules():
    CCS_REACTION_RESULT = dedent("""\
        react ccs_meta_call =
            Ccs.(Execute.Call{proc} | Process{proc}.id | id) 
            ->
            Ccs.(Execute.id | Process{proc}.id | id)
            @[0, 0, 1];

        react ccs_dual =
            Ccs.Execute.((Alt.(Send{action}.id | id)) | (Alt.(Get{action}.id | id)))
            ->
            Ccs.Execute.({action} | id | id)
            @[0, 2];

        react ccs_send =
            Ccs.Execute.((Alt.(Send{action}.id | id)) | id)
            ->
            Ccs.Execute.({action} | id | id)
            @[0, 2];

        react ccs_get =
            Ccs.Execute.((Alt.(Get{action}.id | id)) | id)
            ->
            Ccs.Execute.({action} | id | id)
            @[0, 2];

        react ccs_dual_hidden =
            /hidden Ccs.Execute.(Alt.(Send{hidden}.id | id)) | (Alt.(Get{hidden}.id | id))) | id)
            ->
            Ccs.Execute.(id | id) | id)
            @[0, 2, 4];\n
    """)

    def test_reaction_rules(self):
        inp = FiniteCcsTranslator.CCS_REACTION_RULES
        exp = self.CCS_REACTION_RESULT
        act = "\n".join(map(str, inp)) + "\n"
        assert exp == act


class Test_Ccs_Bigraph():
    def _CCS_BRS_RESULT(self, init: str, rule_names: list[str]) -> str:
        return dedent(f"""\
            begin brs
                init {init};
                rules = [{{{", ".join(rule_names)}}}];
            end
        """)

    def test_empty(self):
        inp = BigraphRepresentation(
            FiniteCcsTranslator.CCS_CONTROLS,
            [],
            [],
        )

        exp = "\n".join([
            Test_Ccs_Controls.CCS_CONTROLS_RESULT,
            "\n", # No bigraphs, so just the empty line
            "\n", # No reaction rules, so just the empty line
            self._CCS_BRS_RESULT("start", [])
        ])

        act = str(inp)
        assert exp == act

    def test_simple(self):
        inp = BigraphRepresentation(
            FiniteCcsTranslator.CCS_CONTROLS,
            [
                BigraphAssignment(
                    "test_proc_def",
                    NestingBigraph(
                        ControlBigraph(
                            ControlByName("C"),
                            [Link("a"), Link("b")]
                        ),
                        IdBigraph()
                    )
                )
            ],
            FiniteCcsTranslator.CCS_REACTION_RULES
        )

        exp = "\n".join([
            Test_Ccs_Controls.CCS_CONTROLS_RESULT,
            "big test_proc_def = (C{a,b}.id);\n",
            Test_Ccs_ReactionRules.CCS_REACTION_RESULT,
            self._CCS_BRS_RESULT("start", ["ccs_meta_call", "ccs_dual", "ccs_send", "ccs_get", "ccs_dual_hidden"])
        ])

        act = str(inp)
        assert exp == act

    def test_two_assignments(self):
        inp = BigraphRepresentation(
            FiniteCcsTranslator.CCS_CONTROLS,
            [
                BigraphAssignment(
                    "a_test_proc",
                    NestingBigraph(
                        ControlBigraph(
                            ControlByName("Get"),
                            [Link("a")]
                        ),
                        IdBigraph()
                    )
                ),

                BigraphAssignment(
                    "b_test_proc",
                    NestingBigraph(
                        ControlBigraph(
                            ControlByName("Send"),
                            [Link("b")]
                        ),
                        IdBigraph()
                    )
                )
            ],
            FiniteCcsTranslator.CCS_REACTION_RULES
        )
        exp = "\n".join([
            Test_Ccs_Controls.CCS_CONTROLS_RESULT,
            "big a_test_proc = (Get{a}.id);",
            "big b_test_proc = (Send{b}.id);\n",
            Test_Ccs_ReactionRules.CCS_REACTION_RESULT,
            self._CCS_BRS_RESULT("start", ["ccs_meta_call", "ccs_dual", "ccs_send", "ccs_get", "ccs_dual_hidden"])
        ])

        act = str(inp)
        assert exp == act

class Test_Translation():
    def test_fail_no_process(self):
        inp = CcsRepresentation(
            [],
            []
        )

        with pytest.raises(ValueError):
            FiniteCcsTranslator(inp, "")._generate_bigraph_content() # pyright: ignore[reportPrivateUsage]

    def test_fail_invalid_process_sum_content(self):
        inp = CcsRepresentation(
            [
                ProcessAssignment(
                    "Test1",
                    SumProcesses([
                        ParallelProcesses([
                            NilProcess()
                        ])
                    ])
                ),
            ],
            []
        )

        with pytest.raises(ValueError):
            FiniteCcsTranslator(inp, "")._generate_bigraph_content() # pyright: ignore[reportPrivateUsage]

    def test_fail_invalid_process_prefix_without_sum(self):
        inp = CcsRepresentation(
            [
                ProcessAssignment(
                    "Test1",
                    PrefixedProcess( # Prefix without sum wrapper
                        Action("a"),
                        NilProcess()
                    )
                ),
            ],
            []
        )

        with pytest.raises(ValueError):
            FiniteCcsTranslator(inp, "")._generate_bigraph_content() # pyright: ignore[reportPrivateUsage]