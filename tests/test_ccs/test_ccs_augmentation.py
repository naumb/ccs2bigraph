"""Bigraph Augmentation Tests"""

from ccs2bigraph.ccs.representation import *
from ccs2bigraph.ccs.augmentation import *

import typing as tp

class Test_Simple_Parent_Augmentation():
    def test_nil_process(self):
        p = NilProcess()
        CcsAugmentor._augment_parents(p) # pyright: ignore[reportPrivateUsage]
        assert p.parent == None

    def test_process_by_name(self):
        p = ProcessByName("Test")
        CcsAugmentor._augment_parents(p) # pyright: ignore[reportPrivateUsage]
        assert p.parent == None

    def test_prefixed_process(self):
        child = NilProcess()
        root = PrefixedProcess(Action("test"), child)
        root = tp.cast(PrefixedProcess, CcsAugmentor._augment_parents(root)) # pyright: ignore[reportPrivateUsage]
        assert root.parent == None
        assert root.remaining.parent == root

    def test_hiding_process(self):
        child = NilProcess()
        root = HidingProcess(child, ActionSet([Action("test")]))
        root = tp.cast(HidingProcess, CcsAugmentor._augment_parents(root)) # pyright: ignore[reportPrivateUsage]
        assert root.parent == None
        assert root.process.parent == root

    def test_renaming_process(self):
        child = NilProcess()
        root = RenamingProcess(child, [(Action("test"), Action("test2"))])
        root = tp.cast(RenamingProcess, CcsAugmentor._augment_parents(root)) # pyright: ignore[reportPrivateUsage]
        assert root.parent == None
        assert root.process.parent == root

    def test_sum_process(self):
        children = [NilProcess()] * 3
        root = SumProcesses(tp.cast(list[Process], children))
        root = tp.cast(SumProcesses, CcsAugmentor._augment_parents(root)) # pyright: ignore[reportPrivateUsage]
        assert root.parent == None
        assert all(child.parent == root for child in root.sums)

    def test_parallel_process(self):
        children = [NilProcess()] * 3
        root = ParallelProcesses(tp.cast(list[Process], children))
        root = tp.cast(ParallelProcesses, CcsAugmentor._augment_parents(root)) # pyright: ignore[reportPrivateUsage]
        assert root.parent == None
        assert all(child.parent == root for child in root.parallels)

class Test_Complex_Parent_Augmentation():
    def test_complex_process(self):
        
        level3s = tp.cast(list[Process], [
            PrefixedProcess(Action("Test"), NilProcess()),
            NilProcess(),
        ])
        level2s = tp.cast(list[Process], [
            HidingProcess(NilProcess(), ActionSet([])),
            RenamingProcess(NilProcess(), []),
            ParallelProcesses(level3s)
        ])
        level1 = SumProcesses(level2s)
        root = PrefixedProcess(Action("Test"), level1)

        root = tp.cast(PrefixedProcess, CcsAugmentor._augment_parents(root)) # pyright: ignore[reportPrivateUsage]

        assert root.parent == None
        assert root.remaining.parent == root
        assert all(s.parent == root.remaining for s in tp.cast(SumProcesses, root.remaining).sums)
        assert tp.cast(HidingProcess, tmp := tp.cast(SumProcesses, root.remaining).sums[0]).process.parent == tmp
        assert tp.cast(RenamingProcess, tmp := tp.cast(SumProcesses, root.remaining).sums[1]).process.parent == tmp
        
        par = tp.cast(ParallelProcesses, tp.cast(SumProcesses, root.remaining).sums[2])
        assert all(p.parent == par for p in par.parallels)

        assert tp.cast(PrefixedProcess, tmp := par.parallels[0]).remaining.parent == tmp


class Test_Simple_Prefix_Augmentation():
    def test_simple_test(self):
        p = PrefixedProcess(Action("test"), NilProcess())
        p = CcsAugmentor._augment_parents(p) # pyright: ignore[reportPrivateUsage]
        p = CcsAugmentor._augment_prefixes(p)  # pyright: ignore[reportPrivateUsage]

        assert p == SumProcesses(
            [
                PrefixedProcess(Action("test"), NilProcess())
            ]
        )

class Test_Process_Augmentation():
    def test_complex_augmentation(self):
        level3s = tp.cast(list[Process], [
            PrefixedProcess(Action("Test"), NilProcess()),
            NilProcess(),
        ])
        level2s = tp.cast(list[Process], [
            HidingProcess(NilProcess(), ActionSet([])),
            RenamingProcess(NilProcess(), []),
            ParallelProcesses(level3s)
        ])
        level1 = SumProcesses(level2s)
        root = PrefixedProcess(Action("Test"), level1)

        root = CcsAugmentor.augment(root)

        assert root == SumProcesses([
            PrefixedProcess(
                Action("Test"),
                SumProcesses([
                    HidingProcess(NilProcess(), ActionSet([])),
                    RenamingProcess(NilProcess(), []),
                    ParallelProcesses([
                        SumProcesses([
                            PrefixedProcess(
                                Action("Test"),
                                NilProcess(),
                            )
                        ]),
                        NilProcess()
                    ])
                ])
            )
        ])