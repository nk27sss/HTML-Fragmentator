# HTML Fragmentator

The main script is [src/split_msg.py](src/split_msg.py).

## Description

Split HTML into fragments by a given maximum number of characters.
Closes or opens the tags from the `BLOCK_TAGS` list when splitting.
Output the result to console. Has several modes of operation

## Usage

```sh
# Split HTML
python3 split_msg.py --max_len <chars> <html_file>
```

```sh
# Split HTML and catch errors and strip and splits text
python3 split_msg.py --catch-err --is-strip --is-splittext --max_len <chars> <html_file>
```

```python
# import function Generator:
>>> from split_msg import split_message
>>> fragments: Generator[str] = split_message(<html_file>, <max_len>, <is_strip>, <is_splittext>)
```

## Arguments

```sh
-e, --catch-err:    Catch errors
-s, --is-strip:     Strip spaces
-t, --is-splittext: Split text
-l, --max-len:      MAX_LEN
source:             Html file
```

## Requirements

- Python 3.12+
- BeautifulSoup4
- click

```
python3 -m pip install -r requirements.txt
```
