import sys
import os.path as path
import glob
import hashlib

import itertools

class Compare():
    def printResult(self, item1: str, item2: str, result: bool = False) -> None:
        if item1 != None and item2 != None:
            header = '[Same]' if result else '[Diff]'
            output = f'{header} {item1} \t{item2}'
        elif item1 != None:
            output = f'[ <- ] {item1}'
        elif item2 != None:
            output = f'[ -> ] {item2}'
        else:
            raise 'Unexpected condition'
        print(output)

    def _compareFiles(self, file1: str, file2: str) -> bool:
        with open(file1, 'rb') as f:
            data = f.read()
            f1md5 = hashlib.md5(data).hexdigest()
        with open(file2, 'rb') as f:
            data = f.read()
            f2md5 = hashlib.md5(data).hexdigest()
        return f1md5 == f2md5

    def _isMatch(self, path1: str, path2: str) -> bool:
        if path.basename(path1) != path.basename(path2):
            return False
        with open(path1, 'rb') as f:
            md5OfItem1 = hashlib.md5(f.read()).hexdigest()
        with open(path2, 'rb') as f:
            md5OfItem2 = hashlib.md5(f.read()).hexdigest()
        return md5OfItem1 == md5OfItem2

    def compareLists(self, list1: set, list2: set) -> tuple:
        matches = set(itertools.product(list1,list2))
        print(f'{len(list1)} items x {len(list2)} items => compare {len(matches)} items')
        if len(matches) < 10000:
            matches = set(filter(lambda tpl: self._isMatch(tpl[0], tpl[1]), matches))
        else:
            for m in matches:
                if self._isMatch(m[0], m[1]):
                    self.printResult(m[0], m[1], True)
        combItem1 = set([x[0] for x in matches])
        combItem2 = set([x[1] for x in matches])
        unmet1 = list1 ^ combItem1
        unmet2 = list2 ^ combItem2
        return (list(matches), list(unmet1), list(unmet2))

    def _getChildrenList(self, item: str) -> list:
        l = []
        if path.isdir(item):
            chPaths = glob.glob(f'{item}/*')
            chPaths.sort(key=lambda x: path.basename(x))
            if not chPaths is None:
                for ch in chPaths:
                    ch = ch.replace('\\', '/')
                    l.extend(self._getChildrenList(ch))
            return l
        else:
            return [item]

    def getItemSets(self, argv) -> tuple:
        item1 = ""
        item2 = ""
        if len(argv) == 3:
            item1 = argv[1]
            item2 = argv[2]
        elif len(argv) == 2:
            item1 = argv[1]
        while item1 == '':
            print('(1) Path of file or directory:')
            item1 = input()
        print(f'Item 1: {item1}')
        while item2 == '':
            print('(2) Path of file or directory:')
            item2 = input()
        print(f'Item 2: {item2}')
        set1 = set(self._getChildrenList(item1))
        set2 = set(self._getChildrenList(item2))
        return (set1, set2)

if __name__ == '__main__':
    comp = Compare()
    (set1, set2) = comp.getItemSets(sys.argv)
    (matches, unmet1, unmet2) = comp.compareLists(set1, set2)
    for item in matches:
        comp.printResult(item[0], item[1], True)
    for item in unmet1:
        comp.printResult(item, None)
    for item in unmet2:
        comp.printResult(None, item)
