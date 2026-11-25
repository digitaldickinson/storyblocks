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

def load(page, name):   # open a fixture the way a student opens a saved build
    page.set_input_files("#importInput", os.path.join(FX, name)); page.wait_for_timeout(150)

LAYERS_NOW = "LAYERS.map(L => L.key + ':' + story[L.key].map(b => b.code + '@' + b.x + '+' + b.len).join(',')).join(' | ')"

with sync_playwright() as p:
    browser = p.chromium.launch(headless="--show" not in sys.argv)
    page = browser.new_page(viewport={"width": 1440, "height": 900}, accept_downloads=True)
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(APP)
    page.evaluate("localStorage.clear()"); page.reload(); page.wait_for_timeout(300)

    print("\nFirst open")
    check(page.evaluate("LAYERS.every(L => !story[L.key].length)") and page.is_visible(".empty"), "a first visit opens on an empty board")
    check(page.locator('[data-act="example"]').count() == 0, "there are no example builds to load")

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
    for medium, fixture in [("video", "example-video-sealife.json"), ("audio", "example-audio-pumpkins.json")]:
        for s, beats in [("basic", ["NEWS", "BECAUSE", "PERSON"]), ("pivot", ["NEWS", "BECAUSE", "PERSON", "AND", "UNSET", "PERSON", "NEXT"])]:
            load(page, fixture)
            lower = "LAYERS.filter(L => L.key !== 'editorial').map(L => story[L.key].map(b => b.code + '@' + b.x + '+' + b.len).join(',')).join(' | ')"
            before, all_before = page.evaluate(lower), page.evaluate(LAYERS_NOW)
            page.click(f'.sbtn[data-arg="{s}"]')
            laid = page.evaluate("story.editorial.map(b => b.code)")
            check(laid == beats and page.evaluate(lower) == before, f"{medium}: {s} lays its beats and leaves the other layers alone", f"laid {laid}")
            page.evaluate("actions.undo()")
            check(page.evaluate(LAYERS_NOW) == all_before, f"{medium}: {s} is one undo step")
    check("seconds" not in page.evaluate("document.body.innerText.replace('not seconds', '')").lower(), "nothing on screen mentions seconds")

    print("\nExport then import round trip")
    for medium, fixture in [("video", "example-video-pumpkins.json"), ("audio", "example-audio-pumpkins.json")]:
        load(page, fixture)
        before = page.evaluate(LAYERS_NOW)
        with page.expect_download() as d: page.click('[data-act="exportFile"]')
        path = os.path.join(tempfile.mkdtemp(), d.value.suggested_filename); d.value.save_as(path)
        page.evaluate("actions.clear()")
        page.set_input_files("#importInput", path); page.wait_for_timeout(150)
        check(page.evaluate(LAYERS_NOW) == before, f"{medium} {fixture} survives export and import")

    print("\nWithout dragging or sight")
    load(page, "oov-sot.json"); page.evaluate("ui.msg = ''; render()")
    sound = page.evaluate("[...document.querySelectorAll('#orderHead ~ h3')].find(h => h.textContent === 'Sound layer').nextElementSibling.innerText.split('\\n')")
    check(sound == ["Gap, 6 studs", "Natural sound, 14 studs", "Gap to the end, 16 studs"], "hidden running order lists the sound layer with its gaps", sound)
    check(page.evaluate("document.querySelector('.sr-only').getBoundingClientRect().width") <= 1, "running order isn't shown on screen")
    oov = page.evaluate("story.script[1].id")
    page.evaluate(f"actions.select('{oov}')")
    x = lambda: page.evaluate(f"find('{oov}').block.x")
    page.click('.tbar [data-act="nudge"][data-arg="1"]'); right = x()
    page.click('.tbar [data-act="nudge"][data-arg="-1"]'); back = x()
    check((right, back) == (7, 6), "toolbar moves a brick by clicks alone", f"x went {right}, {back}")
    page.click('.tbar [data-act="swap"][data-arg="1"]')
    check(page.evaluate("story.script.map(b => b.code)") == ["CUE", "SOT", "OOV", "BACK"], "toolbar swaps a brick by clicks alone")
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

    print("\nPlan the shoot")
    page.evaluate("actions.clear()"); page.wait_for_timeout(50)
    check(page.is_disabled('[data-act="plan"]'), "the plan button is off for an empty build")
    page.evaluate("""(() => { const s = emptyStory(); let x = 0;
      s.editorial = [['NEWS',8],['BECAUSE',10],['PERSON',10]].map(([c,l]) => { const b = newBlock(c, l, x); x += l; return b; });
      s.picture = [newBlock('WS', 8, 0), newBlock('MCU', 10, 18)]; s.sound = [newBlock('NAT', 8, 0)]; s.script = [newBlock('SOT', 10, 18)];
      commit(s); })()""")
    page.click('[data-act="plan"]'); page.wait_for_timeout(100)
    sheet = lambda: page.inner_text(".sheet")
    check(page.is_visible("#plan") and page.evaluate("document.activeElement.classList.contains('pclose')"), "the plan opens with focus on its close button")
    check("Interview 1\nA person explains" in sheet(), "an interview row names the beat it sits under")
    heads = page.evaluate("[...document.querySelectorAll('.pghead')].map(h => h.innerText.split('\\n')[0])")
    check(heads == ["NEWS", "PERSON"], "on-location bricks are grouped under the beat they start in", heads)
    check("Back at base" not in sheet(), "nothing for back at base when the build doesn't call for it")
    check("Press Notice on the board" in sheet(), "notices are listed only once the student has pressed Notice")
    # before typing anything: with something typed, the browser's own undo (rightly) undoes the typing instead
    before = page.evaluate(LAYERS_NOW); page.keyboard.press("Control+z"); page.keyboard.press("Meta+z")
    check(page.evaluate(LAYERS_NOW) == before and page.is_visible("#plan"), "undo shortcuts leave the build alone while the plan is open")
    page.fill('[aria-label="Interview 1: name and role"]', "Sam Jones, driver")
    page.keyboard.press("Escape")
    check(page.is_hidden("#plan") and page.evaluate("document.activeElement.dataset.act") == "plan", "Escape closes it and focus goes back to the button")
    page.evaluate("actions.select(story.script[0].id); actions.nudge(1); actions.deselect()")
    page.click('[data-act="plan"]'); page.wait_for_timeout(100)
    check(page.input_value('[aria-label="Interview 1: name and role"]') == "Sam Jones, driver" and "Interview (sync) · Sam Jones, driver" in sheet(),
          "a typed name survives an edit to the build and shows on the interview's row")
    page.mouse.click(40, 400); page.wait_for_timeout(50)
    check(page.is_hidden("#plan"), "clicking the dimmed backdrop closes it")
    page.click('[data-act="notice"]'); page.click('[data-act="plan"]'); page.wait_for_timeout(100)
    check("Still to decide, from Notice" in sheet() or "Press Notice" not in sheet(), "after Notice, its items (if any) replace the prompt")
    page.emulate_media(media="print")
    check(page.evaluate("getComputedStyle(document.getElementById('app')).display") == "none" and page.is_visible(".sheet") and page.is_hidden(".planbar"),
          "printing shows only the sheet")
    page.emulate_media(media="screen")
    page.once("dialog", lambda d: d.accept()); page.click('[data-act="planClear"]'); page.wait_for_timeout(50)
    check(page.input_value('[aria-label="Interview 1: name and role"]') == "" and page.evaluate("localStorage.getItem('storystack.ws.video')") is None, "Clear empties the plan and its saved entries")
    page.keyboard.press("Escape")
    load(page, "example-audio-pumpkins.json"); page.click('[data-act="plan"]'); page.wait_for_timeout(100)
    check("Recorder or phone charged" in sheet() and "What's in the shot" not in page.inner_html(".sheet") and "Write the track for the ear" in sheet(),
          "audio: the audio kit list, no picture rows, and the track to write")
    page.keyboard.press("Escape")

    print("\nNo JavaScript errors")
    check(not errors, "page ran without errors", "; ".join(errors))
    browser.close()

print(f"\n{passes} passed, {len(failures)} failed")
sys.exit(1 if failures else 0)
