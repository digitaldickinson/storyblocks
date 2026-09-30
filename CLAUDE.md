# StoryBlocks

A browser toy for teaching broadcast story structure. Students build a story as courses of isometric bricks: picture, sound, script and editorial meaning (video), or sound, script and meaning (audio). Brick length is relative (studs), never time. A **Notice** button surfaces observations about the build when the student asks for them.

It's a teaching tool for journalism students at MMU. It is **not** a video editor, a marker or an AI tutor.

## Files

| Path | What it is |
|---|---|
| `storyblocks.html` | The whole app. The only file that ships. |
| `docs/traits.md` | Every brick, its traits, and which Notice rules read which traits. Keep in step with the `TRAITS` table. |
| `docs/notice-principles.md` | The pedagogy behind Notice: Build → Notice → Rebuild. Read before changing any rule or message. |
| `docs/decisions.md` | Design decisions already made, with reasons. Read before proposing to reverse one. |
| `fixtures/` | Saved builds (StoryBlocks export format) and the notices each one should produce. |
| `tests/` | Browser checks. Run them after every change. |
| `archive/` | Earlier versions and the original brief. **History, not instructions.** The original brief contradicts the current design in several places (pre-rendered sprites, SortableJS, packed tracks with no free placement). Do not follow it. |

## Hard constraints

- **One self-contained HTML file.** Inline CSS and JS. No build step, no npm, no frameworks, no external scripts. Google Fonts is the only external request.
- **Vanilla JS, DOM + inline SVG.** No canvas, no three.js.
- **Must work offline and if `localStorage` throws.** Wrap every storage call in try/catch.
- **No brand names** for the construction toy anywhere in the UI, code or comments.
- **UK spelling** throughout.

## How the code is organised (inside `storyblocks.html`)

Rough order, top to bottom:

1. `PAL` colours → `ALL_LAYERS` → `BRICK_ROWS` (the brick list) → `MEDIA` (which layers, examples and wording per medium)
2. `TRAITS`: what each brick means to Notice (see below)
3. State: `story` (one array per layer, each brick `{id, code, len, x}`), `ui`, undo `past`/`future`
4. Model: `put` (drop, shoving touching bricks right), `pushLeft`, `grow`, and `actions`
5. Projection and geometry: `makeView`, `project`, `geom`, `svgBox`, `fitScale`
6. Rendering: `renderStage` (bricks, gaps, highlight bands, grip, toolbar), `layerKey`, `render`, `redrawStage`
7. Notice: `noticeContext`, `NOTICE_RULES`, `runNotice`, `noticePanel`
8. Interaction: click, pointer drag (move, resize, orbit), keyboard, import and export

### The model

- Layers are arrays sorted by `x` (first stud). Bricks never overlap within a layer; gaps are allowed and meaningful.
- Dropping a brick onto others **shoves the touching chain along**; a gap absorbs the shove. Removing or shrinking leaves a gap. This is deliberate: it behaves like real bricks.
- Anything above a gap floats. That's the point, not a bug.

### Traits drive Notice

- **Notice rules never test brick codes.** They test traits (`is(brick, 'voice')`). Adding or changing a brick means giving it traits in `TRAITS`, not editing rules.
- If a new brick needs a rule to treat it differently, prefer a new trait over a special case.
- When you change `TRAITS` or `NOTICE_RULES`, update `docs/traits.md` in the same change.

### Rendering

- The view is an orthographic projection with turn (`az`, 45° = isometric), tilt (`el`) and roll. The turn is limited to about ±20° **on purpose**: beyond that the painter's-order drawing and the three visible faces stop being correct.
- Bricks are drawn left to right within a layer, layers bottom to top. Don't change that order.
- While dragging, redraw only the stage (`scheduleStage`); the full `render()` happens once, on release.
- Brick drag follows the pointer's **horizontal** movement only, corrected for roll. Don't return to the diagonal projection: it felt laggy.

## Don't break existing work

- Saved work lives under `localStorage` keys starting `storystack.` (the old name). **Keep them.** Renaming them would silently wipe every student's saved build.
- Import accepts files with `app` of `storyblocks` **or** `storystack`.
- A renamed brick code goes in `CODE_ALIASES` (e.g. `IV → INVIZ`) so old saves and exports still open.
- Import validates the whole file before changing anything, and says plainly what's wrong. Keep that.

## Pedagogy guard-rails (read `docs/notice-principles.md`)

- **No time.** No seconds, clocks, durations or targets anywhere.
- **No judgement.** No scores, percentages of "good", ticks, traffic lights, pass/fail, "fixes" or model answers. A build with no notices is not "good"; say so if it comes up.
- **Noticing is chosen.** Nothing is analysed while the student builds. Notice runs when pressed; changing the build makes notices stale rather than updating them live.
- **Messages state only what the build shows**: lengths in studs, which bricks, "at the start" / "at the end". No stud numbers (students never see numbers on the board). Interpretive notices are questions, never instructions.
- The design test for any new notice: *does it point at something in this build the student might have overlooked?* and *does it tell them what to decide?* If the second is yes, rethink it.
- Plain, warm wording in anything a student reads. No "error", "wrong", "must", "fail", "correct".

## Accessibility

Target: WCAG 2.2 AA. Full findings, fixes and acceptance checks are in `docs/accessibility.md`; work through them **in priority order**. The principle: *the meaning of a build is its spatial relationships (what's above, below, overlapping, missing), so anything a sighted student can see must be available in another way.*

Must-fix first:

1. **A text version of the build** for screen-reader users: each layer in stud order, gaps included, plus ↑/↓ to move to the brick above or below at the same point.
2. **A non-drag way to move a brick** (WCAG 2.5.7): ← → buttons on the floating toolbar.

Then: skip links, contrast (the dimmed layer key and small brick labels), grip target size, Notice focus and announcement, reflow at narrow widths.

Rules that apply to every change:

- Every control is a real `<button>`/`<input>` with an accessible name. No click handlers on `div`s.
- Anything shown only by colour, position or highlight also exists as text.
- Don't dim text below 4.5:1 (3:1 for large text). Fade decoration, not words.
- Pointer targets at least 24×24px.
- Keep `prefers-reduced-motion` respected.
- Run `python tests/a11y_check.py` as well as `run_tests.py` before saying a UI change is done.

## Working on it

- **Test in a real browser before saying a change works.** Run `python tests/run_tests.py` (see `tests/README.md`). Add a fixture and an expected result when you add or change a rule.
- Look at the result: take a screenshot after visual changes. Several bugs in this project only showed up on screen.
- Keep changes small and say what changed. Don't refactor untouched parts in passing.
- If a request conflicts with a decision in `docs/decisions.md`, say so and ask; don't quietly reverse it.

## Environment notes

Developed on a managed MMU Mac: standard user, no admin, no Homebrew. Python (pyenv) and Node (nvm) are available. System git may refuse to run until the Xcode licence is accepted, which needs admin. Don't suggest installs that need `sudo`.
