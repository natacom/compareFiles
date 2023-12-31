import sys
import os
import os.path as path
import hashlib
from tqdm import tqdm
import logging

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')


class DirectoryComparer():
    def __init__(self, isOutputToFile: bool = True):
        self.__duplicatedFileList = []
        self.__hashMap1 = {}
        self.__hashMap2 = {}
        self.__outputFilepath = None
        if isOutputToFile:
            outputPath = './output.txt'
            num = 1
            while True:
                if path.exists(outputPath):
                    outputPath = f'./output_{num}.txt'
                    num += 1
                else:
                    break
            self.__outputFilepath = outputPath

    def printResult(self, item1: str, item2: str,
                    result: bool = False) -> None:
        if item1 is not None and item2 is not None:
            header = '[Same]' if result else '[Diff]'
            output = f'{header} {item1} \t{item2}'
        elif item1 is not None:
            output = f'[ <- ] {item1}'
        elif item2 is not None:
            output = f'[ -> ] {item2}'
        else:
            raise 'Unexpected condition'

        if self.__outputFilepath is not None:
            filename = self.__outputFilepath
            with open(filename, mode='a', encoding='utf8') as f:
                f.write(output + '\n')
        else:
            print(output)

    def printDuplicatedFiles(self):
        if self.__outputFilepath is not None:
            filename = self.__outputFilepath
            with open(filename, mode='a', encoding='utf8') as f:
                f.write('\n\n===== Duplicated files =====\n')
                for pair in self.__duplicatedFileList:
                    f.write(pair + '\n')
        else:
            for pair in self.__duplicatedFileList:
                print(pair)

    def _compareFiles(self, file1: str, file2: str) -> bool:
        with open(file1, 'rb') as f:
            data = f.read()
            f1md5 = hashlib.md5(data).hexdigest()
        with open(file2, 'rb') as f:
            data = f.read()
            f2md5 = hashlib.md5(data).hexdigest()
        return f1md5 == f2md5

    def _isSame(self, path1: str, path2: str) -> bool:
        with open(path1, 'rb') as f:
            md5OfItem1 = hashlib.md5(f.read()).hexdigest()
        with open(path2, 'rb') as f:
            md5OfItem2 = hashlib.md5(f.read()).hexdigest()
        return md5OfItem1 == md5OfItem2

    def compare(self) -> tuple:
        logging.info('comparing...')
        matches = set()
        for hash, filepath in tqdm(self.__hashMap1.items(), leave=False):
            if hash in self.__hashMap2:
                matches.add((filepath, self.__hashMap2[hash]))
        combItem1 = set([x[0] for x in matches])
        combItem2 = set([x[1] for x in matches])
        unmet1 = set(self.__hashMap1.values()) ^ combItem1
        unmet2 = set(self.__hashMap2.values()) ^ combItem2
        return (list(matches), list(unmet1), list(unmet2))

    def _calculate_hash(self, filepath: str):
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _addFileToHashMap(self, filepath: str, existingMap: dict):
        logging.debug(f"-----_addFileToHashMap {filepath}")
        hash = self._calculate_hash(filepath)
        filepath = filepath.replace('\\', '/')
        if hash not in existingMap:
            logging.debug(existingMap)
            logging.debug(hash)
            existingMap[hash] = filepath
        else:
            org = existingMap[hash]
            new = filepath
            if len(org) <= len(new):
                self.addDuplicatedFile(org, new)
            else:
                existingMap[hash] = new
                self.addDuplicatedFile(new, org)

    def _updateHashMap(self, itemPath: str, existingMap: dict,
                       depth: int = 0) -> None:
        logging.debug('-----entry _updateHashMap')
        if path.isdir(itemPath):
            with os.scandir(itemPath) as it:
                iterator = tqdm(list(it), leave=False) if depth == 0 else \
                            tqdm(list(it), leave=False) if depth == 1 else it
                for entry in iterator:
                    if entry.is_file():
                        # logging.debug('is_file %s', entry.path)
                        self._addFileToHashMap(entry.path, existingMap)
                    elif entry.is_dir():
                        # logging.debug('is_file %s', entry.path)
                        self._updateHashMap(entry.path, existingMap, depth + 1)
        else:
            self._addFileToHashMap(itemPath, existingMap)

    def updateBothHashMaps(self, item1: str, item2: str) -> tuple:
        logging.info('making the hash-filepath map...')
        logging.info(f'Item 1: {item1}')
        self._updateHashMap(item1, self.__hashMap1)
        logging.info(f'Item 2: {item2}')
        self._updateHashMap(item2, self.__hashMap2)

    def addDuplicatedFile(self, file1: str, file2: str) -> None:
        logging.debug('## addDuplicatedFile')
        logging.debug(file1, file2)
        self.__duplicatedFileList.append((file1, file2))
        logging.debug(self.__duplicatedFileList)
        logging.debug('// addDuplicatedFile')

    @property
    def duplicatedFiles(self):
        return self.__duplicatedFileList


def handleArgs(argv) -> tuple:
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
        item1 = item1.strip('"')
    while item2 == '':
        print('(2) Path of file or directory:')
        item2 = input()
        item2 = item2.strip('"')
    return (item1, item2)


if __name__ == '__main__':
    item1, item2 = handleArgs(sys.argv)
    comp = DirectoryComparer()
    comp.updateBothHashMaps(item1, item2)
    logging.info('starting to compare files...')
    (matches, unmet1, unmet2) = comp.compare()
    for item in sorted(list(matches)):
        comp.printResult(item[0], item[1], True)
    for item in sorted(list(unmet1)):
        comp.printResult(item, None)
    for item in sorted(list(unmet2)):
        comp.printResult(None, item)
