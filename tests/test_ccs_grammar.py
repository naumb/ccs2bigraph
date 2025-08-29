"""CCS Grammar Tests"""

import unittest
import pyparsing as pp
import ccs2bigraph.ccs.grammar as g

class Action_Test(unittest.TestCase):
    def test_simple_action(self):
        inp = 'a'
        exp = 'a'
        act = g._action.parse_string(inp) # type: ignore (testing private member)
        self.assertIsInstance(act, pp.ParseResults)
        self.assertEqual(act[0], exp)

    def test_dual_action(self):
        inp = "'a"
        exp = ["'", 'a']
        act = g._action.parse_string(inp) # type: ignore (testing private member)
        self.assertIsInstance(act, pp.ParseResults)
        for (a, e) in zip(act, exp, strict=True): # type: ignore (pyparsing doesn't provide complete type)
            self.assertEqual(a, e)

    def test_long_action(self):
        inp = 'areallylongactionname'
        exp = 'areallylongactionname'
        act = g._action.parse_string(inp) # type: ignore (testing private member)
        self.assertIsInstance(act, pp.ParseResults)
        self.assertEqual(act[0], exp)

    def test_action_with_whitespace(self):
        inp = '  a  '
        exp = 'a'
        act = g._action.parse_string(inp) # type: ignore (testing private member)
        self.assertIsInstance(act, pp.ParseResults)
        self.assertEqual(act[0], exp)

    def test_action_with_uppercase(self):
        inp = 'aBcDe'
        exp = 'aBcDe'
        act = g._action.parse_string(inp) # type: ignore (testing private member)
        self.assertIsInstance(act, pp.ParseResults)
        self.assertEqual(act[0], exp)
    
    def test_invalid_action_name(self):
        inp = 'Invalid'

        with self.assertRaises(pp.exceptions.ParseException):
            g._action.parse_string(inp) # type: ignore (testing private member)

class Set_Test(unittest.TestCase):
    def test_simple_set(self):
        inp = "{a}"
        exp = ['{', 'a', '}']
        act = g._actionset.parse_string(inp) # type: ignore (testing private member)
        self.assertIsInstance(act, pp.ParseResults)
        for (a, e) in zip(act, exp, strict=True): # type: ignore (pyparsing doesn't provide complete type)
            self.assertEqual(a, e)

    def test_long_set(self):
        inp = "{a, b, c, d}"
        exp = ['{', 'a', ',', 'b', ',', 'c', ',', 'd', '}']
        act = g._actionset.parse_string(inp) # type: ignore (testing private member)
        self.assertIsInstance(act, pp.ParseResults)
        for (a, e) in zip(act, exp, strict=True): # type: ignore (pyparsing doesn't provide complete type)
            self.assertEqual(a, e)

class Alternative_Test(unittest.TestCase):
    def test_simple_alternative(self):
        inp = "0 + 0"
        exp = ['0', '+', '0']
        act = g._alternative.parse_string(inp) # type: ignore (testing private member)
        self.assertIsInstance(act, pp.ParseResults) # type: ignore (pyparsing doesn't provide complete type)
        print(act)
        for (a, e) in zip(act, exp, strict=True): # type: ignore (pyparsing doesn't provide complete type)
            self.assertEqual(a, e)

    def test_complex_alternative(self):
        inp = "a.0 + b.0"
        exp = ['a', '.', '0', '+', 'b', '.', '0']
        act = g._alternative.parse_string(inp) # type: ignore (testing private member)
        self.assertIsInstance(act, pp.ParseResults) # type: ignore (pyparsing doesn't provide complete type)
        print(act)
        for (a, e) in zip(act, exp, strict=True): # type: ignore (pyparsing doesn't provide complete type)
            self.assertEqual(a, e)

class Process_Test(unittest.TestCase):
    def test_simple_process(self):
        inp = "A = 0;"
        exp = ['A', '=', '0', ';']
        act = g.parse(inp)
        self.assertIsInstance(act, pp.ParseResults)
        for (a, e) in zip(act, exp, strict=True): # type: ignore (pyparsing doesn't provide complete type)
            self.assertEqual(a, e)

    def test_prefixed_process(self):
        inp = "A = a.0;"
        exp = ['A', '=', 'a', '.', '0', ';']
        act = g.parse(inp)
        self.assertIsInstance(act, pp.ParseResults)
        self.assertNotEqual(len(act), 0)
        for (a, e) in zip(act, exp, strict=True): # type: ignore (pyparsing doesn't provide complete type)
            self.assertEqual(a, e)

    def test_complex_process(self):
        inp = "A = a.'b.0 + 'a.b.0;"
        exp = ['A', '=', 'a', '.', '0', ';']
        act = g.parse(inp)
        self.assertIsInstance(act, pp.ParseResults)
        self.assertNotEqual(len(act), 0)
        for (a, e) in zip(act, exp, strict=True): # type: ignore (pyparsing doesn't provide complete type)
            self.assertEqual(a, e)

if __name__ == '__main__':
    unittest.main()