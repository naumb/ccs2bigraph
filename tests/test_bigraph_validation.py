"""Bigraph Validation Tests"""

import pytest

from ccs2bigraph.bigraph.validation import *
from ccs2bigraph.bigraph.representation import *

class Test_Simple_Bigraph_Validation():
    def test_simple_valid(self):
        inp = BigraphRepresentation(
            [
                ControlDefinition(Control("A", 1)),
                ControlDefinition(AtomicControl("B", 3)),
            ],
            [
                BigraphAssignment(
                    "Test1",
                    ControlBigraph(
                        ControlByName("A"),
                        [Link("a")]
                    )
                ),
                BigraphAssignment(
                    "Test2",
                    ControlBigraph(
                        ControlByName("B"),
                        list(map(Link, ["a", "b", "c"]))
                    )
                ),
            ]
        )
        assert BigraphValidator(inp).validate() == True

    def test_simple_invalid(self):
        inp = BigraphRepresentation(
            [
                ControlDefinition(Control("A", 1)),
                ControlDefinition(AtomicControl("B", 3)),
            ],
            [
                BigraphAssignment(
                    "Test1",
                    ControlBigraph(
                        ControlByName("A"),
                        list(map(Link, ["a", "b", "c"]))
                    )
                ),
                BigraphAssignment(
                    "Test2",
                    ControlBigraph(
                        ControlByName("B"),
                        [Link("a")]
                    )
                ),
            ]
        )
        assert BigraphValidator(inp).validate() == False

    def test_invalid_control(self):
        inp = BigraphRepresentation(
            [
                ControlDefinition(AtomicControl("B", 3)),
            ],
            [
                BigraphAssignment(
                    "Test1",
                    ControlBigraph(
                        ControlByName("A"),
                        list(map(Link, ["a", "b", "c"]))
                    )
                ),
            ]
        )
        assert BigraphValidator(inp).validate() == False

    def test_invalid_too_few_links(self):
        inp = BigraphRepresentation(
            [
                ControlDefinition(AtomicControl("B", 3)),
            ],
            [
                BigraphAssignment(
                    "Test1",
                    ControlBigraph(
                        ControlByName("A"),
                        list(map(Link, ["a", "b"]))
                    )
                ),
            ]
        )
        assert BigraphValidator(inp).validate() == False

    def test_invalid_too_many_links(self):
        inp = BigraphRepresentation(
            [
                ControlDefinition(AtomicControl("B", 3)),
            ],
            [
                BigraphAssignment(
                    "Test1",
                    ControlBigraph(
                        ControlByName("A"),
                        list(map(Link, ["a", "b", "c", "d"]))
                    )
                ),
            ]
        )
        assert BigraphValidator(inp).validate() == False

    def test_id_bigraph(self):
        inp = BigraphRepresentation(
            [
            ],
            [
                BigraphAssignment(
                    "Test1",
                    IdBigraph()
                ),
            ]
        )
        assert BigraphValidator(inp).validate() == True

    def test_invalid_bigraph(self):
        inp = BigraphRepresentation(
            [
            ],
            [
                BigraphAssignment(
                    "Test1",
                    Bigraph()
                ),
            ]
        )

        with pytest.raises(ValueError):
            assert BigraphValidator(inp).validate() == False

class Test_Complex_Bigraph_Validation():
    def test_complex_valid(self):
        inp = BigraphRepresentation(
            list(map(ControlDefinition, [AtomicControl("M", 1), Control("K", 2), Control("L", 0)])),
            [
                BigraphAssignment("Test",
                    ClosedBigraph(
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
                )
            ]
        )
        assert BigraphValidator(inp).validate() == True