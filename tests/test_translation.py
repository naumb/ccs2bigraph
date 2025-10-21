"""
CCS to Bigraph Translation Tests
"""

import pytest

from ccs2bigraph.ccs.representation import *
from ccs2bigraph.translation import FiniteCcsTranslator

class Test_Translation():
    def test_fail_no_process(self):
        inp = CcsRepresentation(
            [],
            []
        )

        with pytest.raises(ValueError):
            FiniteCcsTranslator(inp)._generate_bigraph_content() # pyright: ignore[reportPrivateUsage]

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
            FiniteCcsTranslator(inp)._generate_bigraph_content() # pyright: ignore[reportPrivateUsage]

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
            FiniteCcsTranslator(inp)._generate_bigraph_content() # pyright: ignore[reportPrivateUsage]