import pytest
import compare as target

def test_printResult_both_is_None():
    t = target.Compare()
    with pytest.raises(Exception) as e:
        t.printResult(None, None)

def test_printResult_only_item1(capfd):
    t = target.Compare()

    t.printResult('test', None)
    out, err = capfd.readouterr()
    assert out == '[ <- ] test\n'
    assert err is ''

    t.printResult('test', None, True)
    out, err = capfd.readouterr()
    assert out == '[ <- ] test\n'
    assert err is ''

def test_printResult_only_item2(capfd):
    t = target.Compare()

    t.printResult(None, 'test')
    out, err = capfd.readouterr()
    assert out == '[ -> ] test\n'
    assert err is ''

    t.printResult(None, 'test', True)
    out, err = capfd.readouterr()
    assert out == '[ -> ] test\n'
    assert err is ''

def test_printResult_false(capfd):
    t = target.Compare()
    t.printResult('test1', 'test2')
    out, err = capfd.readouterr()
    assert out == '[Diff] test1 \ttest2\n'
    assert err is ''

def test_printResult_true(capfd):
    t = target.Compare()
    t.printResult('test1', 'test2', True)
    out, err = capfd.readouterr()
    assert out == '[Same] test1 \ttest2\n'
    assert err is ''

def test_compareFiles_same():
    t = target.Compare()
    result = t._compareFiles('./testSample/item1_aaa.txt', './testSample/item2_aaa.txt')
    assert result is True

def test_compareFiles_diff():
    t = target.Compare()
    result = t._compareFiles('./testSample/item1_aaa.txt', './testSample/item3_abc.txt')
    assert not result is True

def test_difDir_one_file():
    t = target.Compare()
    tree = t._getChildrenList('./testSample/dir1/dir1-1/item_aaa.txt')
    assert tree == ['./testSample/dir1/dir1-1/item_aaa.txt']

def test_difDir_one_dir():
    t = target.Compare()
    tree = t._getChildrenList('./testSample/dir1/dir1_empty')
    assert tree == []

def test_difDir_recursive():
    t = target.Compare()
    tree = t._getChildrenList('./testSample')
    expected = [
        './testSample/dir1/dir1-1/item_aaa.txt',
        './testSample/dir1/dir1-1/item_abc.txt',
        './testSample/dir2/dir2-1/item_aaa.txt',
        './testSample/dir2/dir2-1/item_abc.txt',
        './testSample/dir2/dir2-2/item_abc.txt',
        './testSample/dir2/item_aaa.txt',
        './testSample/dir2/item_abc.txt',
        './testSample/item1_aaa.txt',
        './testSample/item2_aaa.txt',
        './testSample/item3_abc.txt',
    ]
    assert tree == expected

def test_compareLists_oneFile_same():
    t = target.Compare()
    set1 = set(t._getChildrenList('./testSample/dir1/dir1-1/item_aaa.txt'))
    set2 = set(t._getChildrenList('./testSample/dir2/item_aaa.txt'))
    (matches, unmet1, unmet2) = t.compareLists(set1, set2)
    expectedMatches = [
        ('./testSample/dir1/dir1-1/item_aaa.txt',
         './testSample/dir2/item_aaa.txt'),
    ]
    expectedUnmet1 = []
    expectedUnmet2 = []
    assert matches.sort() == expectedMatches.sort()
    assert unmet1.sort() == expectedUnmet1.sort()
    assert unmet2.sort() == expectedUnmet2.sort()

def test_compareLists_oneFile_diff():
    t = target.Compare()
    set1 = set(t._getChildrenList('./testSample/dir1/dir1-1/item_aaa.txt'))
    set2 = set(t._getChildrenList('./testSample/dir2/item_abc.txt'))
    (matches, unmet1, unmet2) = t.compareLists(set1, set2)
    expectedMatches = []
    expectedUnmet1 = ['./testSample/dir1/dir1-1/item_aaa.txt']
    expectedUnmet2 = ['./testSample/dir2/item_abc.txt']
    assert matches.sort() == expectedMatches.sort()
    assert unmet1.sort() == expectedUnmet1.sort()
    assert unmet2.sort() == expectedUnmet2.sort()

def test_compareLists_oneDir_same():
    t = target.Compare()
    set1 = set(t._getChildrenList('./testSample/dir1/dir1-1'))
    set2 = set(t._getChildrenList('./testSample/dir2/dir2-1'))
    (matches, unmet1, unmet2) = t.compareLists(set1, set2)
    expectedMatches = [
        ('./testSample/dir1/dir1-1/item_aaa.txt',
         './testSample/dir2/dir2-1/item_aaa.txt'),
        ('./testSample/dir1/dir1-1/item_abc.txt',
         './testSample/dir2/dir2-1/item_abc.txt'),
    ]
    expectedUnmet1 = []
    expectedUnmet2 = []
    assert matches.sort() == expectedMatches.sort()
    assert unmet1.sort() == expectedUnmet1.sort()
    assert unmet2.sort() == expectedUnmet2.sort()

def test_compareLists_oneDir_both():
    t = target.Compare()
    set1 = set(t._getChildrenList('./testSample/dir1/dir1-1'))
    set2 = set(t._getChildrenList('./testSample/dir2/dir2-2'))
    (matches, unmet1, unmet2) = t.compareLists(set1, set2)
    expectedMatches = [
        ('./testSample/dir1/dir1-1/item_abc.txt',
         './testSample/dir2/dir2-2/item_abc.txt'),
    ]
    expectedUnmet1 = ['./testSample/dir1/dir1-1/item_aaa.txt']
    expectedUnmet2 = []
    assert matches.sort() == expectedMatches.sort()
    assert unmet1.sort() == expectedUnmet1.sort()
    assert unmet2.sort() == expectedUnmet2.sort()
