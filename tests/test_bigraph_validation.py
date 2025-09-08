"""Bigraph Validation Tests"""

from ccs2bigraph.bigraph.validation import *
from ccs2bigraph.bigraph.representation import *

class Test_Simple_Bigraph_Validation():
    def test_simple_valid(self):
        inp = BigraphValidator(
            BigraphRepresentation(
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
        )
        assert inp.validate() == True

    def test_simple_invalid(self):
        inp = BigraphValidator(
            BigraphRepresentation(
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
        )
        assert inp.validate() == False

    def test_invalid_control(self):
        inp = BigraphValidator(
            BigraphRepresentation(
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
        )
        assert inp.validate() == False
