# type: ignore

"""Doctests

This file's purpose is to include all doctests in unittest
"""

import doctest

import ccs2bigraph.ccs.representation
import ccs2bigraph.bigraph.representation

def load_tests(loader, tests, ignore):
    # Fügt alle Doctests aus mod.foo als Unittest-Testsuite hinzu
    tests.addTests(doctest.DocTestSuite(ccs2bigraph.bigraph.representation))
    tests.addTests(doctest.DocTestSuite(ccs2bigraph.ccs.representation))
    return tests