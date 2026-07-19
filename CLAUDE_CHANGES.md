# Claude-generated changes to `src/main.py`

This file explains what I (Claude) changed in your code. Everything I touched
is also marked directly in `main.py` with `# Claude-generated` comments, so
you can find it in context too.

## 1. Implemented the TODO: `chunk_text()`

```python
def chunk_text(text, chunk_size=500, overlap=50):
    ...
```

How it works:
- It uses a sliding window over the string `text`.
- Each chunk is `chunk_size` characters long.
- After grabbing a chunk, the window moves forward by `chunk_size - overlap`
  characters instead of a full `chunk_size`. That's what makes the chunks
  overlap — the last `overlap` characters of one chunk reappear at the
  start of the next one.
- The loop stops once `start` reaches the end of the text.
- I added simple `ValueError` checks for bad arguments (`chunk_size <= 0`,
  negative `overlap`, or `overlap >= chunk_size`), since any of those would
  otherwise cause the loop to misbehave (e.g. never advance, or advance
  backwards).

Example: `chunk_text("abcdefghij", chunk_size=4, overlap=1)` returns
`['abcd', 'defg', 'ghij', 'j']` — you can see `'d'` and `'g'` repeated at
the boundaries.

Defaults (`chunk_size=500`, `overlap=50`) are just reasonable starting
points for feeding chunks into an AI model later — feel free to tune them.

## 2. Fixed a pre-existing bug in `get_text_from_page()`

This wasn't part of the TODO, but I noticed it while wiring `chunk_text()`
into the pipeline, so I fixed it too:

```python
def get_text_from_page(doc):
    for page in doc:
        text = page.get_text()
    return text
```

The loop reassigned `text` on every iteration, so after the loop finished,
`text` only held the **last page's** content — every other page's text was
overwritten and lost.

I changed it to collect each page's text into a list and join them at the
end, so all pages are kept:

```python
pages_text = []
for page in doc:
    pages_text.append(page.get_text())
text = "\n".join(pages_text)
```

## 3. Wired `chunk_text()` into `main()`

`main()` now calls `chunk_text(text)` on the extracted text and prints how
many chunks were produced, then returns the list of chunks so it can be
reused later (e.g. sent to an AI model).

## Not changed

- `open_file()` — untouched.
- `requirements.txt` — untouched.
- No new dependencies were added; `chunk_text()` only uses plain Python
  string slicing.
