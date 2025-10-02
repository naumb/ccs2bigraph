"""
CCS to Bigraph Translation Tests
"""

import pytest

from ccs2bigraph.ccs.representation import *
from ccs2bigraph.bigraph.representation import BigraphRepresentation
from ccs2bigraph.translation import FiniteCcsTranslator

class Test_Translation():
    def test_fail_no_process(self):
        inp = CcsRepresentation(
            [],
            []
        )

        with pytest.raises(AssertionError):
            FiniteCcsTranslator(inp)._generate_bigraph_content() # pyright: ignore[reportPrivateUsage]

    def test_fail_too_many_processes(self):
        inp = CcsRepresentation(
            [
                ProcessAssignment(
                    "Test1",
                    NilProcess()
                ),
                ProcessAssignment(
                    "Test2",
                    NilProcess()
                ),
            ],
            []
        )

        with pytest.raises(AssertionError):
            FiniteCcsTranslator(inp)._generate_bigraph_content() # pyright: ignore[reportPrivateUsage]

    def test_fail_invalid_process(self):
        inp = CcsRepresentation(
            [
                ProcessAssignment(
                    "Test1",
                    SumProcesses
                ),
            ],
            []
        )

        with pytest.raises(AssertionError):
            FiniteCcsTranslator(inp)._generate_bigraph_content() # pyright: ignore[reportPrivateUsage]

    