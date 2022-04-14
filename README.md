# compareFiles
Compare files in given directories by using md5.

## usage
If you run this command,
```python
python3 compare.py .\testSample\dir1\ .\testSample\dir3\
```
then this app shall print this
```
Item 1: .\testSample\dir1\
Item 2: .\testSample\dir3\
[Same] ./testSample/dir1/dir1-1/item_aaa.txt    ./testSample/dir3/item_aaa.txt
[Same] ./testSample/dir1/dir1-1/item_aaa.txt    ./testSample/dir3/test.txt
[ <- ] ./testSample/dir1/dir1-1/item_abc.txt
[ -> ] ./testSample/dir3/item_xxx.txt
```
because the directory tree is this.
```
testSample
- dir1
  - dir1_empty
  - dir1-1
    - item_aaa.txt   <<< the content is 'aaa'
    - item_abc.txt   <<< the content is 'abc'
- dir3
  - item_aaa.txt     <<< the content is 'aaa'
  - test.txt         <<< the content is 'aaa'
  - item_xxx.txt     <<< the content is 'xxx'
```
