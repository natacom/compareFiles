import pytest
import compare as target
import timeit

# Test data
# ---------------
# - ./testSample
#   - dir1
#     - dir1_empty
#     - dir1-1
#       - item_aaa.txt      | aaa
#       - item_abc.txt      | abc
#   - dir2
#     - dir2-1
#       - item_abc.txt      | abc
#       - item_aaa.txt      | aaa
#     - dir2-2
#       - item_ccc.txt      | ccc
#     - item_aaa.txt        | aaa
#     - item_abc.txt        | abc
#   - dir3
#     - item_aaa.txt        | aaa
#     - item_xxx.txt        | xxx
#     - test.txt            | aaa
#   - item1_aaa.txt         | aaa
#   - item2_aaa.txt         | aaa
#   - item3_abc.txt         | abc


def test_printResult_both_is_None():
    comparer = target.DirectoryComparer(isOutputToFile=False)
    with pytest.raises(Exception):
        comparer.printResult(None, None)


def test_printResult_only_item1(capfd):
    comparer = target.DirectoryComparer(isOutputToFile=False)

    comparer.printResult('test', None)
    out, err = capfd.readouterr()
    assert out == '[ <- ] test\n'
    assert err == ''

    comparer.printResult('test', None, True)
    out, err = capfd.readouterr()
    assert out == '[ <- ] test\n'
    assert err == ''


def test_printResult_only_item2(capfd):
    comparer = target.DirectoryComparer(isOutputToFile=False)

    comparer.printResult(None, 'test')
    out, err = capfd.readouterr()
    assert out == '[ -> ] test\n'
    assert err == ''

    comparer.printResult(None, 'test', True)
    out, err = capfd.readouterr()
    assert out == '[ -> ] test\n'
    assert err == ''


def test_printResult_false(capfd):
    comparer = target.DirectoryComparer(isOutputToFile=False)
    comparer.printResult('test1', 'test2')
    out, err = capfd.readouterr()
    assert out == '[Diff] test1 \ttest2\n'
    assert err == ''


def test_printResult_true(capfd):
    comparer = target.DirectoryComparer(isOutputToFile=False)
    comparer.printResult('test1', 'test2', True)
    out, err = capfd.readouterr()
    assert out == '[Same] test1 \ttest2\n'
    assert err == ''


def test_compareFiles_same():
    # - ./testSample
    #   - item1_aaa.txt
    #   - item2_aaa.txt
    comparer = target.DirectoryComparer(isOutputToFile=False)
    result = comparer._compareFiles('./testSample/item1_aaa.txt',
                                    './testSample/item2_aaa.txt')
    assert result is True


def test_compareFiles_diff():
    # - ./testSample
    #   - item1_aaa.txt         | aaa
    #   - item3_abc.txt         | abc
    comparer = target.DirectoryComparer(isOutputToFile=False)
    result = comparer._compareFiles('./testSample/item1_aaa.txt',
                                    './testSample/item3_abc.txt')
    assert result is not True


def test_diffDir_one_file():
    comparer = target.DirectoryComparer(isOutputToFile=False)
    map = {}
    comparer._updateHashMap('./testSample/dir1/dir1-1/item_aaa.txt', map)
    assert list(map.values()) == ['./testSample/dir1/dir1-1/item_aaa.txt']


def test_diffDir_one_dir():
    comparer = target.DirectoryComparer(isOutputToFile=False)
    map = {}
    comparer._updateHashMap('./testSample/dir1/dir1_empty', map)
    assert list(map.values()) == []


def test_diffDir_recursive():
    # - ./testSample
    #   - dir2
    #     - dir2-1
    #       - item_abc.txt      | abc
    #       - item_aaa.txt      | aaa
    #     - dir2-2
    #       - item_ccc.txt      | ccc
    #     - item_aaa.txt        | aaa
    #     - item_abc.txt        | abc
    comparer = target.DirectoryComparer(isOutputToFile=False)
    map = {}
    comparer._updateHashMap('./testSample/dir2', map)

    expected = [
        './testSample/dir2/item_aaa.txt',
        './testSample/dir2/item_abc.txt',
        './testSample/dir2/dir2-2/item_ccc.txt',
    ].sort()
    assert list(map.values()).sort() == expected

    # duplicated map
    expectedDuplicatedFiles = [
        ('./testSample/dir2/item_aaa.txt',
         './testSample/dir2/dir2-1/item_aaa.txt'),
        ('./testSample/dir2/item_abc.txt',
         './testSample/dir2/dir2-1/item_abc.txt'),
    ]
    assert list(comparer.duplicatedFiles) == expectedDuplicatedFiles


def test_compareLists_oneFile_same():
    # - ./testSample
    #   - dir1
    #     - dir1-1
    #       - item_aaa.txt      | aaa
    #   - dir2
    #     - item_aaa.txt        | aaa
    comparer = target.DirectoryComparer(isOutputToFile=False)
    comparer.updateBothHashMaps(
        './testSample/dir1/dir1-1/item_aaa.txt',
        './testSample/dir2/item_aaa.txt')
    (matches, unmet1, unmet2) = comparer.compare()
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
    # - ./testSample
    #   - dir1
    #     - dir1_empty
    #     - dir1-1
    #       - item_aaa.txt      | aaa
    #   - dir2
    #     - item_abc.txt        | abc
    comparer = target.DirectoryComparer(isOutputToFile=False)
    comparer.updateBothHashMaps(
        './testSample/dir1/dir1-1/item_aaa.txt',
        './testSample/dir2/item_abc.txt')
    (matches, unmet1, unmet2) = comparer.compare()
    expectedMatches = []
    expectedUnmet1 = ['./testSample/dir1/dir1-1/item_aaa.txt']
    expectedUnmet2 = ['./testSample/dir2/item_abc.txt']
    assert matches.sort() == expectedMatches.sort()
    assert unmet1.sort() == expectedUnmet1.sort()
    assert unmet2.sort() == expectedUnmet2.sort()


def test_compareLists_oneDir_same():
    # - ./testSample
    #   - dir1
    #     - dir1-1
    #       - item_aaa.txt      | aaa
    #       - item_abc.txt      | abc
    #   - dir2
    #     - dir2-1
    #       - item_abc.txt      | abc
    #       - item_aaa.txt      | aaa
    comparer = target.DirectoryComparer(isOutputToFile=False)
    comparer.updateBothHashMaps(
        './testSample/dir1/dir1-1',
        './testSample/dir2/dir2-1')
    (matches, unmet1, unmet2) = comparer.compare()
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
    # - ./testSample
    #   - dir1
    #     - dir1-1
    #       - item_aaa.txt      | aaa
    #       - item_abc.txt      | abc
    #     - dir2-2
    #       - item_abc.txt      | abc
    comparer = target.DirectoryComparer(isOutputToFile=False)
    comparer.updateBothHashMaps(
        './testSample/dir1/dir1-1',
        './testSample/dir2/dir2-2')
    (matches, unmet1, unmet2) = comparer.compare()
    expectedMatches = [
        ('./testSample/dir1/dir1-1/item_abc.txt',
         './testSample/dir2/dir2-2/item_abc.txt'),
    ]
    expectedUnmet1 = ['./testSample/dir1/dir1-1/item_aaa.txt']
    expectedUnmet2 = []
    assert matches.sort() == expectedMatches.sort()
    assert unmet1.sort() == expectedUnmet1.sort()
    assert unmet2.sort() == expectedUnmet2.sort()


def func_operation():
    comparer = target.DirectoryComparer(isOutputToFile=False)
    comparer.updateBothHashMaps('./testSample/dir1', './testSample/dir2')
    (matches, unmet1, unmet2) = comparer.compare()


# You can see elapsed time if you run the test with the option -s.
def test_check_time():
    elapsed_time = timeit.timeit(func_operation, number=5)
    print(f'Elapsed time is {elapsed_time}.')
    assert True
