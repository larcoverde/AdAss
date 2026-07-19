# Claude-generated changes to `src/main.py` — embeddings fix

## What was wrong
`main()` was calling `generate_embeddings(chunks)` and storing the result in
`vectors`, but then returning only `chunks` — so every embedding computed was
immediately thrown away when `main()` ended. Nothing downstream could ever
use them.

## What changed

1. **`generate_embeddings()`** — added `device="cpu"` explicitly to the
   `SentenceTransformer(...)` call. Given your laptop has no real GPU, this
   just makes sure sentence-transformers doesn't waste time
   auto-detecting/attempting a GPU device that isn't usable.

2. **`main()`** — instead of discarding `vectors`, it now zips `chunks` and
   `vectors` together into a list of `(chunk_text, embedding)` pairs and
   returns that:

   ```python
   chunks_with_vectors = list(zip(chunks, vectors))
   return chunks_with_vectors
   ```

   This matters because the next step (similarity search) needs to know
   *which chunk* a matched embedding belongs to — if you keep them as two
   separate lists, that link can get lost or misaligned. Zipping keeps each
   chunk permanently paired with its own vector.

## Not changed
- `open_file()`, `get_text_from_page()`, `chunk_text()` — untouched from
  last time.
- No caching added yet — every run still re-embeds from scratch (still on
  your TODO list).

## Commit
Nothing here changes behavior in a risky way — it's a straightforward bugfix
plus a small safety default. Suggested commit:

```
git add src/main.py
git commit -m "fix: keep chunks paired with embeddings, force CPU for encoding"
```
