# Tests

`run_tests.py` opens `storyblocks.html` in a headless Chromium and checks that:

- every fixture produces exactly its expected notices;
- bad files are refused;
- old exports still open;
- export and import round-trip;
- there are no JavaScript errors.

## One-off setup

No admin rights needed; everything installs into your home folder.

```
python -m pip install playwright
python -m playwright install chromium
```

The second line downloads a copy of Chromium (about 150 MB) into `~/Library/Caches/ms-playwright`.

## Running

From the project folder:

```
python tests/run_tests.py          # headless
python tests/run_tests.py --show   # watch it in a browser window
```

It prints `ok` or `FAIL` for each check, and exits with 1 if anything failed.

## When a rule changes on purpose

`fixtures/expected.json` lists, for each fixture, the rule ids Notice should produce, in the order it shows them. If you change a rule deliberately, a test *should* fail. Check that the new result is the one you intended, then update that entry in `expected.json` by hand. Don't regenerate the whole file blind: the failures are the point.

## Adding a case

1. Build it in StoryBlocks and use **Export**, or write the JSON by hand. The fixtures show the format, and an `_about` field is ignored on import, so use it to say what the case is for.
2. Save it in `fixtures/`.
3. Add its expected rule ids under `"valid"` in `expected.json`.
