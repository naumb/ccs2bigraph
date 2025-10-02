"""CCS Representation Tests"""

from ccs2bigraph.ccs.representation import *

class Test_Actions():
    def test_simple_action(self):
        inp = Action("a")
        exp = "a"
        act = str(inp)
        assert exp == act

    def test_dual_action(self):
        inp = DualAction("a")
        exp = "'a"
        act = str(inp)
        assert exp == act

    def test_action_set(self):
        inp = ActionSet(list(map(Action, ["a", "b", "c"])))
        exp = r"{a, b, c}"
        act = str(inp)
        assert exp == act

    def test_action_set_by_name(self):
        inp = ActionSetByName("Test")
        exp = "Test"
        act = str(inp)
        assert exp == act

    def test_action_set_assignment(self):
        inp = ActionSetAssignment("Test", ActionSet(list(map(Action, ["a", "b", "c"]))))
        exp = "set Test = {a, b, c};"
        act = str(inp)
        assert exp == act

class Test_Processes():
    def test_nil_process(self):
        assert "0" == str(NilProcess())

    def test_process_by_name(self):
        inp = ProcessByName("Test")
        exp = "Test"
        act = str(inp)
        assert exp == act

    def test_prefixed_process(self):
        inp = PrefixedProcess(Action("a"), NilProcess())
        exp = "(a.0)"
        act = str(inp)
        assert exp == act

    def test_hiding_process_actionset(self):
        inp = HidingProcess(ProcessByName("A"), ActionSet(list(map(Action, ["a", "b"]))))
        exp = r"(A \ {a, b})"
        act = str(inp)
        assert exp == act

    def test_hiding_process_actionsetbyname(self):
        inp = HidingProcess(ProcessByName("A"), ActionSetByName("H"))
        exp = r"(A \ H)"
        act = str(inp)
        assert exp == act

    def test_renaming_process(self):
        inp = RenamingProcess(ProcessByName("A"), [(Action("new"), Action("old"))])
        exp = r"(A[new/old])"
        act = str(inp)
        assert exp == act

    def test_sum_processes(self):
        inp = SumProcesses([NilProcess(), ProcessByName("A")])
        exp = r"(0 + A)"
        act = str(inp)
        assert exp == act

    def test_parallel_processes(self):
        inp = ParallelProcesses([NilProcess(), ProcessByName("A")])
        exp = r"(0 | A)"
        act = str(inp)
        assert exp == act

    def test_process_assignment(self):
        inp = ProcessAssignment("Test", NilProcess())
        exp = "Test = 0;"
        act = str(inp)
        assert exp == act