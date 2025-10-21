"""Bigraph Representation Tests"""

from ccs2bigraph.bigraph.representation import *

class Test_Control():
    def test_simple_control(self):
        inp = ControlDefinition(Control("A", 0))
        exp = "ctrl A = 0;"
        act = str(inp)
        assert exp == act

    def test_arity_control(self):
        inp = ControlDefinition(Control("A", 42))
        exp = "ctrl A = 42;"
        act = str(inp)
        assert exp == act

    def test_atomic_control(self):
        inp = ControlDefinition(AtomicControl("A", 0))
        exp = "atomic ctrl A = 0;"
        act = str(inp)
        assert exp == act

    def test_atomic_arity_control(self):
        inp = ControlDefinition(AtomicControl("A", 42))
        exp = "atomic ctrl A = 42;"
        act = str(inp)
        assert exp == act

    def test_control_by_name(self):
        inp = ControlByName("A")
        exp = "A"
        act = str(inp)
        assert exp == act

class Test_Link():
    def test_simple_link(self):
        inp = Link("a")
        exp = "a"
        act = str(inp)
        assert exp == act

class Test_Bigraph():
    def test_one_bigraph(self):
        inp = OneBigraph()
        exp = "1"
        act = str(inp)
        assert exp == act

    def test_id_bigraph(self):
        inp = IdBigraph()
        exp = "id"
        act = str(inp)
        assert exp == act

    def test_control_bigraph(self):
        inp = ControlBigraph(ControlByName('A'), [Link('a')])
        exp = r"A{a}"
        act = str(inp)
        assert exp == act

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
        assert exp == act

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
        assert exp == act

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
        assert exp == act

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
        assert exp == act
    
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
        assert exp == act

    def test_parallel_bigraph(self):
        inp = ParallelBigraphs([
            ControlBigraph(
                ControlByName("A"),
                []
            ),
            ControlBigraph(
                ControlByName("B"),
                []
            ),
        ])
        exp = r"(A || B)"
        act = str(inp)
        assert exp == act

    def test_multi_parallel_bigraph(self):
        inp = ParallelBigraphs([
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
        exp = r"(A || B || C || D)"
        act = str(inp)
        assert exp == act

    def test_parallel_link_bigraph(self):
        inp = ParallelBigraphs([
            ControlBigraph(
                ControlByName("A"),
                [Link("a")]
            ),
            ControlBigraph(
                ControlByName("B"),
                [Link("b")]
            ),
        ])
        exp = r"(A{a} || B{b})"
        act = str(inp)
        assert exp == act
    
    def test_multi_parallel_link_bigraph(self):
        inp = ParallelBigraphs([
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
        exp = r"(A{b,c,d} || B{a,c,d} || C{a,b,d} || D{a,b,c})"
        act = str(inp)
        assert exp == act

class Test_Assignment():
    def test_assignment(self):
        inp = BigraphAssignment(
            "Test",
            ParallelBigraphs([
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
        )
        exp = "big Test = (A{b,c,d} || B{a,c,d} || C{a,b,d} || D{a,b,c});"
        act = str(inp)
        assert exp == act

    def test_bigraphbyname(self):
        inp = BigraphByName("A")
        exp = "A"
        act = str(inp)
        assert exp == act

class Test_Complex_Bigraph():
    def test_01(self):
        inp = ClosedBigraph(
            Link("x"), 
            ClosedBigraph(
                Link("z"),
                ClosedBigraph(
                    Link("w"),
                    ParallelBigraphs([
                        NestingBigraph(
                            ControlBigraph(
                                ControlByName("M"),
                                [Link("x")]
                            ),
                            MergedBigraphs([
                                NestingBigraph(
                                    ControlBigraph(
                                        ControlByName("K"),
                                        [Link("x"), Link("z")]
                                    ),
                                    OneBigraph()
                                ),
                                NestingBigraph(
                                    ControlBigraph(
                                        ControlByName("L"),
                                        []
                                    ),
                                    NestingBigraph(
                                        ControlBigraph(
                                            ControlByName("K"),
                                            [Link("z"), Link("w")]
                                        ),
                                        OneBigraph()
                                    )
                                )
                            ])
                        ),
                        NestingBigraph(
                            ControlBigraph(
                                ControlByName("K"),
                                [Link("w"), Link("x")]
                            ),
                            NestingBigraph(
                                ControlBigraph(
                                    ControlByName("M"),
                                    [Link("w")]
                                ),
                                OneBigraph()
                            )
                        )
                    ])
                )
            )
        )
        exp = r"(/x (/z (/w ((M{x}.((K{x,z}.1) | (L.(K{z,w}.1)))) || (K{w,x}.(M{w}.1))))))"
        act = str(inp)
        assert exp == act

class Test_Ccs_Bigraph():
    from textwrap import dedent

    _CCS_CONTROLS = [
        ControlDefinition(AtomicControl("Nil", 0)),
        ControlDefinition(Control("Alt", 0)),
        ControlDefinition(Control("Send", 1)),
        ControlDefinition(Control("Get", 1)),
    ]

    _CCS_CONTROLS_RESULT = dedent("""\
        atomic ctrl Nil = 0;
        ctrl Alt = 0;
        ctrl Send = 1;
        ctrl Get = 1;
    """)
    
    _CCS_REACTION_RESULT = dedent("""\
        react ccs_react = 
            (Alt.(Send{a}.id | id)) | (Alt.(Get{a}.id | id))
            ->
            {a} | id | id
            @[0, 2];
    """)
    
    def _CCS_BRS_RESULT(self, init: str) -> str:
        return dedent(f"""\
            begin brs
                init {init};
                rules = [{{ccs_react}}];
            end
        """)

    def test_empty(self):
        inp = BigraphRepresentation(
            self._CCS_CONTROLS,
            [],
            BigraphByName("Bogus")
        )

        exp = "\n".join([
            self._CCS_CONTROLS_RESULT,
            "\n", # No bigraphs, so just the empty line
            self._CCS_REACTION_RESULT,
            self._CCS_BRS_RESULT("Bogus")
        ])

        act = str(inp)
        assert exp == act

    def test_simple(self):
        inp = BigraphRepresentation(
            self._CCS_CONTROLS,
            [
                BigraphAssignment(
                    "Test",
                    NestingBigraph(
                        ControlBigraph(
                            ControlByName("C"),
                            [Link("a"), Link("b")]
                        ),
                        IdBigraph()
                    )
                )
            ],
            BigraphByName("Test")
        )

        exp = "\n".join([
            self._CCS_CONTROLS_RESULT,
            "big Test = (C{a,b}.id);\n",
            self._CCS_REACTION_RESULT,
            self._CCS_BRS_RESULT("Test")
        ])

        act = str(inp)
        assert exp == act

    def test_two_assignments(self):
        inp = BigraphRepresentation(
            self._CCS_CONTROLS,
            [
                BigraphAssignment(
                    "A",
                    NestingBigraph(
                        ControlBigraph(
                            ControlByName("C1"),
                            [Link("a"), Link("b")]
                        ),
                        IdBigraph()
                    )
                ),

                BigraphAssignment(
                    "B",
                    NestingBigraph(
                        ControlBigraph(
                            ControlByName("C2"),
                            [Link("c"), Link("d")]
                        ),
                        IdBigraph()
                    )
                )
            ],
            BigraphByName("A")
        )
        exp = "\n".join([
            self._CCS_CONTROLS_RESULT,
            "big A = (C1{a,b}.id);",
            "big B = (C2{c,d}.id);\n",
            self._CCS_REACTION_RESULT,
            self._CCS_BRS_RESULT("A")
        ])

        act = str(inp)
        assert exp == act

