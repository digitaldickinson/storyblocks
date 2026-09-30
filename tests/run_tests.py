"""StoryBlocks browser checks.

Opens storyblocks.html in a headless browser and checks:
  1. every fixture in fixtures/ imports, and produces exactly the notices in fixtures/expected.json
  2. invalid files are refused with the right message and change nothing
  3. an old export (brick 'IV', app 'storystack') opens with the brick as INVIZ
  4. export then import gives back the same build
  5. the page throws no JavaScript errors

Run from the project folder:   python tests/run_tests.py
Add --show to watch it in a visible browser window.
Exit code is 0 if everything passes, 1 otherwise.
"""
import json, os, sys, tempfile
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = "file://" + os.path.join(ROOT, "storyblocks.html")
FX = os.path.join(ROOT, "fixtures")
expected = json.load(open(os.path.join(FX, "expected.json")))
failures, passes = [], 0

def check(ok, label, detail=""):
    global passes
    if ok: passes += 1; print(f"  ok    {label}")
    else: failures.append(label); print(f"  FAIL  {label}  {detail}")

LAYERS_NOW = "LAYERS.map(L => L.key + ':' + story[L.key].map(b => b.code + '@' + b.x + '+' + b.len).join(',')).join(' | ')"

with sync_playwright() as p:
    browser = p.chromium.launch(headless="--show" not in sys.argv)
    page = browser.new_page(viewport={"width": 1440, "height": 900}, accept_downloads=True)
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(APP)
    page.evaluate("localStorage.clear()"); page.reload(); page.wait_for_timeout(300)

    print("\nFixtures: notices")
    for name, want in expected["valid"].items():
        page.set_input_files("#importInput", os.path.join(FX, name)); page.wait_for_timeout(150)
        opened = page.evaluate("ui.msg").startswith("Opened")
        got = page.evaluate("runNotice().map(i => i.id)")
        check(opened and got == want, name, f"\n        expected {want}\n        got      {got}" + ("" if opened else f"\n        import said: {page.evaluate('ui.msg')}"))

    print("\nInvalid files are refused and change nothing")
    for name, msg in expected["invalid"].items():
        before = page.evaluate(LAYERS_NOW)
        page.set_input_files("#importInput", os.path.join(FX, name)); page.wait_for_timeout(150)
        said = page.evaluate("ui.msg")
        check(said.startswith(msg) and page.evaluate(LAYERS_NOW) == before, name, f"said: {said!r}")

    print("\nOld exports still open")
    page.set_input_files("#importInput", os.path.join(FX, "old-export-iv.json")); page.wait_for_timeout(150)
    check(page.evaluate("story.picture.map(b => b.code)") == ["INVIZ"], "IV becomes INVIZ")

    print("\nExport then import round trip")
    for medium, key in [("video", "pkg"), ("audio", "rpkg")]:
        page.evaluate(f"setMedium('{medium}')"); page.evaluate(f"actions.example('{key}')")
        before = page.evaluate(LAYERS_NOW)
        with page.expect_download() as d: page.click('[data-act="exportFile"]')
        path = os.path.join(tempfile.mkdtemp(), d.value.suggested_filename); d.value.save_as(path)
        page.evaluate("actions.clear()")
        page.set_input_files("#importInput", path); page.wait_for_timeout(150)
        check(page.evaluate(LAYERS_NOW) == before, f"{medium} {key} survives export and import")

    print("\nNo JavaScript errors")
    check(not errors, "page ran without errors", "; ".join(errors))
    browser.close()

print(f"\n{passes} passed, {len(failures)} failed")
sys.exit(1 if failures else 0)
