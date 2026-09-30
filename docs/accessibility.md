# Accessibility

Target: **WCAG 2.2 AA**. Audited on 30 September 2026 with axe-core 4, a keyboard walk-through and a narrow-screen check.

**Summary.** The basics are sound: real buttons throughout, named bricks, full keyboard editing, visible focus, text notices and reduced motion. The serious gap is that the *meaning* of a build (what sits above, below and alongside what, and where the gaps are) is only available visually. Fix that first.

## What already works (keep it)

- axe-core reports **no violations** on the main view.
- Every control, brick and palette card is a real `<button>` with an accessible name. A brick's name gives its brick name, layer, length and start: "Presenter in vision, picture layer, 6 studs, starts at stud 0".
- Keyboard: Tab to a brick; Enter selects; `[` `]` resize; ← → nudge; Shift+← → swap; ↑ ↓ move to the brick above or below; Delete removes (leaving a gap); Escape deselects; Ctrl/Cmd+Z undoes. Focus stays on the brick after each change.
- Visible focus ring on bricks and controls.
- Notices are text. The highlight on the build adds to them rather than replacing them.
- `prefers-reduced-motion` switches off animation.
- A polite live region (`#live`) announces messages.
- `lang="en"` and a page title are set.

## Findings and fixes, in priority order

### 1. The build can't be perceived without sight (must fix)

**Status (30 September 2026): done, except the optional `aria-describedby`.** A running order for screen readers only (hidden on screen, under a "Running order" heading) lists each layer, top to bottom, with its bricks and gaps. A visible panel was tried and dropped: it added little for sighted students. Stage bricks are grouped by layer, and ↑/↓ moves between layers (a gap is announced). Still to do: the VoiceOver check under "Done when".

**Problem.** For a screen-reader user the stage is a flat list of buttons. Gaps don't exist for them, and there's no way to find what sits above or below a brick, which is the whole point of the tool. (WCAG 1.3.1 Info and Relationships.)

**Fix.**

- A **text running order** of the build, one list per layer, in stud order, **gaps included**. For example: "Sound: gap, 6 studs; Natural sound, 14 studs; Interview (sync), 10 studs." A toggleable panel is better than visually hidden text, because it's useful to everyone as a check on the picture. It updates on every change.
- **↑ / ↓ on a focused brick** moves focus to the brick in the layer above or below that covers the same stud. If there's a gap there, announce it: "Nothing in the sound layer here."
- Put each layer's bricks in a group (`role="group"`, `aria-label="Sound layer"`) so screen readers can navigate layer by layer.
- Consider adding what's above and below to a brick's accessible description (`aria-describedby`), e.g. "Under it: Voiceover. Over it: Wide shot."

**Done when:** with VoiceOver on (Cmd+F5) and the screen off, someone can describe the OOV/SOT example's structure, including the gap under the cue and the OOV running into the SOT.

### 2. Moving a brick needs dragging or a keyboard (must fix)

**Status (30 September 2026): done.** The toolbar has ← → (one stud) and « » (swap with the brick before or after).

**Problem.** The floating toolbar lets a mouse user add or remove studs, duplicate and remove, but not move. A student who can't drag (tremor, trackpad, switch access) and doesn't use the keyboard can't move anything. (WCAG 2.5.7 Dragging Movements.)

**Fix.** Add **← 1 stud** and **1 stud →** buttons to the toolbar, calling `actions.nudge(-1 / 1)`. Optionally add "Swap earlier / later" to an overflow.

**Done when:** every edit (move, resize, swap, duplicate, remove) can be done with clicks alone, no dragging.

### 3. Too many Tab stops before the build

**Problem.** Keyboard users press Tab **41 times** (through the whole brick box) to reach the first brick, and **61 times** to reach Notice. (WCAG 2.4.1 Bypass Blocks.)

**Fix.** Add skip links at the top, visible on focus: "Skip to the build" and "Skip to Notice". Optionally, give the brick box one Tab stop per layer group, with arrow keys moving within it.

**Done when:** the first brick and the Notice button are each three Tab presses or fewer from the top.

### 4. Contrast

**Status (30 September 2026): the layer key is done** (its mini-bricks fade, its words don't). The brick labels inside the SVG are still to do.

**Problems.**

- **The dimmed layer key.** When a brick is selected, the other key rows drop to opacity 0.4, which puts their text at **2.55:1**. This is axe's only failure. (1.4.3)
- **Brick labels inside the SVG**, which axe can't check:
  - editorial plate labels are 7 to 10px;
  - white on teal (MUS) and on pink (BREATHE) is just under 4.5:1.

**Fix.**

- Dim the key's mini-bricks, not its text. Show the active row with a background or border instead.
- Give editorial labels a minimum of 9px, or drop the label (the name is in the accessible name and the toolbar) when the plate is too thin.
- Darken the teal and pink fronts slightly, or use dark ink on them.

**Done when:** axe reports no contrast failures, and every brick label measures at least 4.5:1 against its face colour.

### 5. Resize grip target size

**Status (30 September 2026): done** (26px).

**Problem.** The round grip is 22×22px. (2.5.8 Target Size, minimum 24×24px.)

**Fix.** Make it 26px, or give it a larger invisible hit area around it.

### 6. Notice panel focus and announcement

**Problem.** Opening Notice doesn't move focus to the panel or announce anything, so a screen-reader user may not know it opened. The same goes for the stale state.

**Fix.**

- On opening, move focus to the panel heading (`tabindex="-1"`) and announce "3 notices" through `#live`.
- When the notices go stale, announce "You've changed the build since" once.
- Escape closes the panel and returns focus to the Notice button.

### 7. No reflow at narrow widths or high zoom

**Problem.** At 390px wide (a phone), or a laptop at 200% zoom, the stage stays about 1,000px wide, and because the page itself doesn't scroll, the layout is unusable. (1.4.10 Reflow.)

**Fix.** Below about 900px:

- the brick box becomes a closed drawer or a bottom sheet by default;
- the stage takes the full width;
- the header controls wrap or collapse into a menu.

Test at 320px and at 200% browser zoom.

### 7a. The Notice panel can cover the selected brick

**Problem.** Notice floats over the stage. When it's open over the selected brick, it hides the grip and part of the toolbar. (2.4.11 Focus Not Obscured; 2.5.8.)

**Fix.** Not decided. Options: dock Notice as a column beside the stage; or move the toolbar and grip clear of it.

### 8. Pointer-only view turning (accept for now)

Turning, tilting and rolling the view is mouse- or touch-only. It isn't needed to do anything and there's a reset, so this is acceptable. If it's easy, add keys (for example Alt+arrows) later.

## How to check

- `python tests/a11y_check.py` runs axe-core against the main states (nothing selected; a brick selected with Notice open; audio mode) and reports violations. See `tests/README.md`.
- axe can't judge meaning or SVG text. After any UI change, also:
  1. Unplug the mouse and do a full edit with the keyboard: add, move, resize, remove, Notice, import, export.
  2. With VoiceOver on, listen to the OOV/SOT example.
  3. Check at 200% browser zoom.
