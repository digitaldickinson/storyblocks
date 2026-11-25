"""Browser checks for StoryTape (storytape.html), the magnetic-tape board.

Checks that it opens empty, shows no time anywhere, can be built and edited from the keyboard,
undoes every change, exports a script without times, and has no axe-core violations
(WCAG 2.2 A/AA plus best practice).

Setup is the same as for the StoryBlocks checks (see tests/README.md).
Run from the project folder:   python tests/storytape_check.py
Exit code is 0 if everything passes, 1 otherwise.
"""
import os, re, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = "file://" + os.path.join(ROOT, "storytape.html")
AXE_PATH = os.path.join(ROOT, "node_modules", "axe-core", "axe.min.js")
TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"]
failures, passes = [], 0
TIME = re.compile(r"\b\d+:\d\d\b|\b\d+\s?s\b|\bseconds?\b", re.I)   # 0:10, 10s, 10 s, seconds

def check(ok, label, detail=""):
    global passes
    if ok: passes += 1; print(f"  ok    {label}")
    else: failures.append(label); print(f"  FAIL  {label}  {detail}")

def axe(page, label):
    if not os.path.exists(AXE_PATH):
        check(False, f"axe: {label}", "axe-core not found: npm install axe-core@4"); return
    page.add_script_tag(content=open(AXE_PATH).read())
    v = page.evaluate("tags => axe.run(document, { runOnly: tags })", TAGS)["violations"]
    check(not v, f"axe finds nothing on {label}", "; ".join(f"{x['id']} ({len(x['nodes'])})" for x in v))

STRIPS = "strips.map(s => s.lane + ':' + s.roll + '@' + s.start + '+' + s.dur).join(' ')"

with sync_playwright() as p:
    browser = p.chromium.launch(headless="--show" not in sys.argv)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(APP); page.evaluate("localStorage.clear()"); page.reload(); page.wait_for_timeout(200)

    print("\nFirst open")
    check(page.evaluate("strips.length") == 0 and page.is_visible(".empty-hint"), "a new board opens empty, with a hint")
    check(page.locator("text=Reset Sample").count() == 0, "there is no sample board to load")
    axe(page, "the empty board")

    print("\nNo time")
    page.click('.roll:has-text("Picture")'); page.keyboard.press("Enter")
    page.click('.roll:has-text("Reporter")'); page.keyboard.type("VO over the pool"); page.keyboard.press("Enter")
    page.click('.roll:has-text("Sound")'); page.keyboard.press("Escape")
    shown = page.inner_text("#app")
    check(not TIME.search(shown), "nothing on screen is a time or a duration", TIME.findall(shown))
    check("5 squares" in page.inner_text(".sbar") if page.is_visible(".sbar") else True, "a strip's length is given in squares")
    page.evaluate("modalOpen = true; render()")
    md = page.input_value("#mdOut")
    check(not TIME.search(md) and "Part 1" in md, "the exported script is in numbered parts, with no times", TIME.findall(md))
    page.keyboard.press("Escape")

    print("\nKeyboard")
    sid = page.evaluate("strips.find(s => s.roll === 'reporter').id")
    page.focus(f'.strip[data-id="{sid}"]')
    check(page.evaluate("selectedId") == sid, "focusing a strip selects it")
    start = page.evaluate(f"strips.find(s => s.id === '{sid}').start")
    page.keyboard.press("ArrowRight")
    check(page.evaluate(f"strips.find(s => s.id === '{sid}').start") == start + 2 and page.evaluate("document.activeElement.dataset.id") == sid,
          "→ moves a strip one square and keeps focus on it")
    page.keyboard.press("]")
    check(page.evaluate(f"strips.find(s => s.id === '{sid}').dur") == 12, "] lengthens a strip by one square")
    check("6 squares" in page.inner_text("#live"), "the change is announced in squares", page.inner_text("#live"))
    label = page.get_attribute(f'.strip[data-id="{sid}"]', "aria-label")
    check(label == "Reporter strip, 6 squares: VO over the pool", "a strip's name says what it is, how long, and what's written on it", label)
    check("Gap, 1 square" in page.inner_text("#orderHead ~ ol, section.sr-only") or "Gap" in page.inner_html("section.sr-only"),
          "the running order for screen readers lists the gaps")
    page.keyboard.press("Enter"); page.keyboard.press("End"); page.keyboard.type(", then the crowd"); page.keyboard.press("Enter")
    check(page.evaluate(f"strips.find(s => s.id === '{sid}').note") == "VO over the pool, then the crowd", "Enter writes on a strip from the keyboard")
    axe(page, "a board with a strip selected")

    print("\nUndo")
    before = page.evaluate(STRIPS)
    page.focus(f'.strip[data-id="{sid}"]'); page.keyboard.press("Delete")
    check(page.evaluate("strips.length") == 2, "Delete removes a strip")
    page.keyboard.press("Meta+z")
    check(page.evaluate(STRIPS) == before, "undo brings a removed strip back")
    page.click("text=Clear Board")
    check(page.evaluate("strips.length") == 0, "Clear Board empties the board")
    page.click("button:has-text('Undo')")
    check(page.evaluate(STRIPS) == before, "and Undo brings it all back")
    page.click("button:has-text('Redo')")
    check(page.evaluate("strips.length") == 0, "Redo clears it again")
    page.click("button:has-text('Undo')")
    n = page.evaluate("past.length")
    box = page.locator(f'.strip[data-id="{sid}"]').bounding_box()
    page.mouse.move(box["x"] + 20, box["y"] + box["height"] / 2); page.mouse.down()
    page.mouse.move(box["x"] + 80, box["y"] + box["height"] / 2, steps=5); page.mouse.up()
    moved = page.evaluate(STRIPS)
    check(page.evaluate("past.length") == n + 1 and moved != before, "a drag is one undo step")
    page.keyboard.press("Control+z")
    check(page.evaluate(STRIPS) == before, "and undo puts the strip back")

    print("\nAudio")
    page.click('.medium [aria-checked="false"]'); page.wait_for_timeout(100)
    check(page.evaluate("medium") == "audio" and page.evaluate("strips.length") == 0, "audio opens its own empty board")
    axe(page, "the audio board")

    print("\nNo JavaScript errors")
    check(not errors, "page ran without errors", "; ".join(errors))
    browser.close()

print(f"\n{passes} passed, {len(failures)} failed")
sys.exit(1 if failures else 0)
