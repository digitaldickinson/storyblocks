"""Automated accessibility check for StoryBlocks, using axe-core (WCAG 2.2 A/AA plus best practice).

Checks three states: video example with nothing selected; a brick selected with Notice open; audio mode.
axe can't judge whether the build's *meaning* is available without sight, or check text inside the
bricks' SVG. See docs/accessibility.md for the manual checks that cover those.

One-off setup, from the project folder (needs Node, no admin):   npm install axe-core@4
Run:   python tests/a11y_check.py
Exit code is 0 with no violations, 1 otherwise.
"""
import os, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = "file://" + os.path.join(ROOT, "storyblocks.html")
AXE_PATH = os.path.join(ROOT, "node_modules", "axe-core", "axe.min.js")
if not os.path.exists(AXE_PATH):
    sys.exit("axe-core not found. From the project folder run:  npm install axe-core@4")
AXE = open(AXE_PATH).read()
TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"]
total = 0

def run(page, label):
    global total
    page.add_script_tag(content=AXE)
    res = page.evaluate("tags => axe.run(document, { runOnly: tags })", TAGS)
    v = res["violations"]; total += len(v)
    print(f"\n{label}: {'no violations' if not v else f'{len(v)} rule(s) violated'}")
    for x in v:
        print(f"  [{x['impact']}] {x['id']}: {x['help']}  ({len(x['nodes'])} element{'s' if len(x['nodes']) != 1 else ''})")
        for n in x["nodes"][:3]:
            print(f"      {n['target']}  {(n.get('failureSummary') or '').splitlines()[-1].strip()[:140]}")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto(APP); page.evaluate("localStorage.clear()"); page.reload(); page.wait_for_timeout(300)

    page.evaluate("setMedium('video'); actions.example('oov'); ui.msg = ''; render()")
    run(page, "Video example, nothing selected")

    brick = page.evaluate("story.sound[0].id")
    page.evaluate(f"ui.sel = '{brick}'; render()"); page.click('[data-act="notice"]'); page.wait_for_timeout(200)
    run(page, "Brick selected, Notice open")

    page.evaluate("ui.sel = null; ui.notice = null; setMedium('audio'); actions.example('rpkg'); ui.msg = ''; render()")
    run(page, "Audio example")
    browser.close()

print(f"\n{total} violation(s) in total")
sys.exit(1 if total else 0)
