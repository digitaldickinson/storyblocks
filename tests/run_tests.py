"""StoryBlocks browser checks.

Opens storyblocks.html in a headless browser and checks:
  1. every fixture in fixtures/ imports, and produces exactly the notices in fixtures/expected.json
  2. invalid files are refused with the right message and change nothing
  3. an old export (brick 'IV', app 'storystack') opens with the brick as INVIZ
  3a. starting structures replace only the structure layer, as one undo step
  4. export then import gives back the same build
  5. the build can be read and edited without dragging or sight (hidden running order, toolbar, arrows)
  6. the page throws no JavaScript errors

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

    print("\nStarting structures")
    for medium, key in [("video", "sea"), ("audio", "rpump")]:
        for s, beats in [("basic", ["NEWS", "BECAUSE", "PERSON"]), ("pivot", ["NEWS", "BECAUSE", "PERSON", "AND", "UNSET", "PERSON", "NEXT"])]:
            page.evaluate(f"setMedium('{medium}'); actions.example('{key}')")
            lower = "LAYERS.filter(L => L.key !== 'editorial').map(L => story[L.key].map(b => b.code + '@' + b.x + '+' + b.len).join(',')).join(' | ')"
            before, all_before = page.evaluate(lower), page.evaluate(LAYERS_NOW)
            page.click(f'.sbtn[data-arg="{s}"]')
            laid = page.evaluate("story.editorial.map(b => b.code)")
            check(laid == beats and page.evaluate(lower) == before, f"{medium}: {s} lays its beats and leaves the other layers alone", f"laid {laid}")
            page.evaluate("actions.undo()")
            check(page.evaluate(LAYERS_NOW) == all_before, f"{medium}: {s} is one undo step")
    check("seconds" not in page.evaluate("document.body.innerText.replace('not seconds', '')").lower(), "nothing on screen mentions seconds")

    print("\nExport then import round trip")
    for medium, key in [("video", "pump"), ("audio", "rpump")]:
        page.evaluate(f"setMedium('{medium}')"); page.evaluate(f"actions.example('{key}')")
        before = page.evaluate(LAYERS_NOW)
        with page.expect_download() as d: page.click('[data-act="exportFile"]')
        path = os.path.join(tempfile.mkdtemp(), d.value.suggested_filename); d.value.save_as(path)
        page.evaluate("actions.clear()")
        page.set_input_files("#importInput", path); page.wait_for_timeout(150)
        check(page.evaluate(LAYERS_NOW) == before, f"{medium} {key} survives export and import")

    print("\nWithout dragging or sight")
    page.evaluate("setMedium('video'); actions.example('oov'); ui.msg = ''; render()")
    sound = page.evaluate("[...document.querySelectorAll('#orderHead ~ h3')].find(h => h.textContent === 'Sound layer').nextElementSibling.innerText.split('\\n')")
    check(sound == ["Gap, 6 studs", "Natural sound, 14 studs", "Interview (sync), 10 studs", "Gap to the end, 6 studs"], "hidden running order lists the sound layer with its gaps", sound)
    check(page.evaluate("document.querySelector('.sr-only').getBoundingClientRect().width") <= 1, "running order isn't shown on screen")
    oov = page.evaluate("story.script[1].id")
    page.evaluate(f"actions.select('{oov}')")
    x = lambda: page.evaluate(f"find('{oov}').block.x")
    page.click('.tbar [data-act="nudge"][data-arg="1"]'); right = x()
    page.click('.tbar [data-act="nudge"][data-arg="-1"]'); back = x()
    check((right, back) == (7, 6), "toolbar moves a brick by clicks alone", f"x went {right}, {back}")
    page.click('.tbar [data-act="swap"][data-arg="1"]')
    check(page.evaluate("story.script.map(b => b.code)") == ["CUE", "RUN", "OOV", "BACK"], "toolbar swaps a brick by clicks alone")
    page.evaluate("actions.undo(); ui.sel = null; actions.select(story.script[1].id)")
    label = lambda: page.evaluate("document.activeElement.getAttribute('aria-label') || ''")
    page.keyboard.press("ArrowDown"); down = label()
    page.keyboard.press("ArrowUp"); page.keyboard.press("ArrowUp"); up = label()
    check(down.startswith("Natural sound") and up.startswith("Because"), "up and down arrows move between layers", f"down: {down!r}, up: {up!r}")
    page.evaluate("focusBrick(story.script[0].id)"); page.keyboard.press("ArrowDown")
    check(page.evaluate("ui.msg") == "Nothing in the sound layer below this brick.", "a gap below is announced", page.evaluate("ui.msg"))

    page.evaluate("ui.sel = null; render()"); page.click('.pcard[data-arg="WS"]'); page.wait_for_timeout(300)
    spot = page.evaluate("""(() => { const plate = document.getElementById('world').firstElementChild, r = plate.getBoundingClientRect();
      for (let y = r.bottom - 5; y > r.top; y -= 7) for (let x = r.left + 5; x < r.right; x += 7) {
        const e = document.elementFromPoint(x, y); if (e && plate.contains(e)) return [x, y]; } })()""")
    page.mouse.click(*spot); page.wait_for_timeout(100)
    check(page.evaluate("ui.sel") is None, "clicking the baseplate lets a new brick go")

    print("\nNo JavaScript errors")
    check(not errors, "page ran without errors", "; ".join(errors))
    browser.close()

print(f"\n{passes} passed, {len(failures)} failed")
sys.exit(1 if failures else 0)
