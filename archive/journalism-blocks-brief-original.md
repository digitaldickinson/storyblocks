# Journalism Blocks — build brief

Build **Journalism Blocks**, a single-page browser app that helps journalism students see how technical craft decisions (shots, sound) combine into an editorial whole. It uses a construction-brick visual metaphor.

This is not a video editor. Nothing plays, imports media or renders video. It is closer to a paper edit that students can handle physically.

The one design test for every decision:

> Does this help a student see how individual craft decisions combine to produce an editorial whole?

If a feature makes the app more like an NLE without improving that understanding, leave it out.

---

## Priority: feel before mechanics

The core product is: **bricks, three tracks, compound bricks, resizing, unlocking, and the X-Ray view.** Get these feeling *delightful* before anything else.

Delightful means:
- snappy resize with stud snapping,
- satisfying drop and insert animations,
- the unlock moment visibly separating the compound,
- X-Ray exploding smoothly and reassembling.

If those work, the product works.

**Do not over-engineer positioning** just because the model could support it. Section 1 deliberately keeps positioning simple: packed tracks, order is the model. Do not add free placement, gaps, nudging, collision handling, snapping between tracks or any general constraint solving. If you find yourself writing layout maths beyond "sum the lengths of the bricks before this one", stop and ask.

Patterns, insights, the overview and persistence are secondary. Build them properly, but after the core feels right.

---

## 0. Hard constraints

- **One file: `index.html`.** Inline CSS and JS. No build step, no npm, no local dependencies.
- External scripts come **only from cdnjs**, with pinned versions:
  - **interact.js**: edge-drag resizing with grid snapping, and dragging compounds and multi-track patterns onto valid drop points.
  - **SortableJS**: reordering within a track, and dragging single bricks from the library into a track.
  - Nothing else without asking me first.
- Vanilla JS. No framework.
- Render with **DOM + CSS**. No canvas, no three.js. Bricks must be focusable, keyboard-operable and screen-reader-labelled.
- Persist to `localStorage`, wrapped in try/catch. The app must work if storage throws.
- Do not use the word "LEGO" anywhere in the UI, metadata or comments. The bricks are generic construction bricks.

Structure the JS in clearly marked sections, in this order:
`CONFIG` (vocabularies, patterns, rules) → `MODEL` (pure state and operations, no DOM) → `ANALYSIS` (pure functions over the model) → `RENDER` → `INTERACTION` → `PERSISTENCE` → `BOOT`.

Editorial rules must never appear in event handlers or render code.

---

## 1. The model (read this carefully — it is the core of the app)

### 1.1 Relative length, not time

The unit is the **stud**. A stud is an abstract unit of relative length. It is **not** a second.

- The app **never shows seconds** in the MVP: no clock, no ruler in seconds, no target duration, and no "cut to time" features.
- What matters is **relative length** across tracks. If the reporter script runs under the whole piece, it has to be as long as the picture above it. If the councillor's brick is three times the resident's, that is an editorial statement the student can see.
- The model stores lengths as integer studs so that tracks share one scale. A later toggle may map 1 stud to 1 second. Leave a `CONFIG.studUnit` hook for this, but do not build it.

### 1.2 Three tracks

A story has three **tracks**: `picture`, `sound`, `editorial`.

Each track is an **ordered, packed array** of blocks. Every block has an integer `length` in studs.

- **Array order is the only source of truth for position.** A block's `start` is derived (the sum of the lengths of the blocks before it in the same track). It is never stored or edited directly.
- A **boundary** is any stud where a block starts or ends in a track. A **shared boundary** is a stud that is a boundary in all three tracks. Stud 0 always qualifies; an empty track's only boundary is 0.
- There are no gaps and no free placement. Use a Silence brick if a student wants deliberate quiet.
- Tracks are independent. Picture and sound boundaries do **not** have to line up. Sound running across a picture cut (J/L-cuts, SOT under GVs) is one of the main things the app teaches, and packed tracks of different brick lengths produce it naturally.

### 1.3 Mismatch is shown, never fixed

When tracks differ in overall length or don't cover each other (script overhanging the pictures, pictures running on with nothing underneath), the app **shows** it and **never auto-stretches or auto-fits** to resolve it.

- Render any overhang clearly. For example, the part of a track that extends past the others sits over bare baseplate, with a subtle hatched marker on the empty tracks above or below it.
- Noticing the mismatch is the learning moment. Do not remove it for the student.

### 1.4 Editorial is a track of spans, not an attribute of shots

Editorial blocks are **spans** on their own track. Each span covers a range and carries a function (claim, evidence…).

Do **not** store editorial meaning on picture blocks. The meaning of a shot depends on what is said and shown around it, not on its framing.

A span may be **unassigned**. This is a state, not a function: it is drawn as a grey dashed span, has no lens, counts as "no editorial span" for coverage and rules, and is excluded from lens breakdowns. It is stored as the editorial type key `unassigned` with `lens: null`.

### 1.5 Groups: compound bricks

A `group` links blocks across tracks so that they move and resize together. A group has at most one member per track and at least two members. **A group existing means it is locked**; there is no unlocked group state.

The canonical example is **Interview SOT**. In news, an interview SOT is conventionally an MCU. Adding "Interview SOT" from the library therefore creates, in one action:

- an MCU on `picture`,
- a SOT on `sound`,
- an unassigned span on `editorial`,

all with the same `length` (the sound member's default) and a shared `groupId`.

**Inserting compounds.** A compound (or a multi-track pattern) may only be inserted at a **shared boundary**. It is inserted at that stud in every track, so its members always start together. **Never create a group that is drifted on arrival**, and never silently drop something at stud 0 or mid-sequence.

- **Drag:** while a compound is being dragged, highlight only the valid drop points (shared boundaries). Dropping elsewhere does nothing.
- **Add button:**
  - If a brick is selected: insert at the shared boundary nearest to the selected brick's start (ties go to the later boundary). With a multi-selection, use the most recently selected brick.
  - If nothing is selected and all three tracks end at the same stud: append at that stud.
  - Otherwise: do not insert. Highlight the valid drop points and show: "Your tracks end at different points — drag the compound to where you want it."
  - After inserting, briefly flash the new group so the student sees where it went.

**Behaviour of a group:**

- **Resize:** all members resize as one unit.
- **Moving by keyboard (←/→):** each member moves one place in its own track.
- **Moving by drag:** the dragged member moves to its drop index. Every other member moves the same number of places in its own track, clamped to the ends of that track.
- Because neighbouring bricks differ in length, after a move the members may no longer start at the same stud. Do **not** solve this. Mark the group as **drifted** (a visual tear in the group connector) and offer two actions in the inspector: **Realign** and **Unlock**. This is consistent with 1.3: mismatch is shown, not silently fixed. Drift is derived, never stored.
- **Realign:** the anchor is the member the student last moved (`groups[id].anchorId`; if missing, the picture member; if there is no picture member, the first member present in track order picture → sound → editorial). In each other track, move **only that group's member** to the index whose start equals the anchor's start. Do not move any other bricks. If no such index exists in some track, do not change anything. Say so in plain words (e.g. "The sound track has no cut at the point where this picture starts, so these can't be lined up by reordering") and offer Unlock.
- **Unlock** (in the inspector) dissolves the group. The student can then replace part of the MCU with a CU or GVs while the SOT continues underneath. This is the lesson: the default teaches the convention, and unlocking teaches the craft.
- **Re-lock** from a multi-selection: at most one block per track, at least two blocks, all starting at the same stud and with the same length. Otherwise the inspector explains plainly why they can't be locked.

### 1.6 Operations

All operations are pure functions in `MODEL`. Each returns a new state. Undo and redo use a state history stack of about 50 entries. Every operation below is exactly one undo step, including inserting a pattern and each step of the five-shot cycle.

With packed tracks, every operation is an array operation. Positions fall out of the render.

- **insert(track, index, block)**
- **insertCompound(compoundKey, stud)** — `stud` must be a shared boundary.
- **move(blockId, ±1)**: swap with the neighbour in the track.
- **moveTo(blockId, index)**: move to an index within the same track (from drag).
- **resize(blockId, newLength)**: minimum 1.
- **duplicate, remove**
- **setType(blockId, type)**: switch type within the same track.
- **updateFields(blockId, { voice, contributor, notes })**
- **lockSelection(blockIds)**, **unlock(groupId)**, **realign(groupId)**
- **insertPattern(patternKey, target)**
- **cycleFiveShot(patternId)**
- **loadStory(story)**: replace the whole story (example, empty, import).
- **Group rule:** resize, remove and duplicate apply to every member of a group. move and moveTo follow 1.5, and set `anchorId` to the member the student moved. Duplicating a group inserts each copy directly after its original and gives the copies a new group.

That is the entire operation set. Do not add positional machinery (nudging, gaps, free placement, cross-track snapping).

### 1.7 Default lengths

Every library brick drops in with a sensible default length, so students never *have* to think about length before placing a brick. Resizing is there for the student who notices an imbalance.

Suggested defaults (in `CONFIG`, easy to change):

| Brick | Studs |
|---|---|
| WS, GV | 5 |
| MS, MCU | 5 |
| CU, ECU, Detail, OTS | 4 |
| Graphic | 6 |
| PTC | 8 |
| Reporter track | 10 |
| SOT | 10 |
| Atmos, Natural sound | 3 |
| Music bed | 8 |
| Silence | 2 |
| Editorial spans | the length of the picture block at the span's start, else 5 |
| Compounds | the sound member's default (Interview SOT 10, PTC 10) |

Patterns do **not** use these defaults. Each pattern sets an explicit length for every brick (see 8).

### 1.8 Schema

```js
// block (its track is the array it lives in; there is no track or order field)
{
  id,
  type,            // key into CONFIG vocabularies for that track, e.g. "MCU", "SOT", "claim", "unassigned"
  length,          // integer studs (relative units, not seconds), >= 1
  groupId: null,   // shared id for compound bricks
  voice: null,     // sound only: "reporter"|"authority"|"affected"|"expert"|"vox"|null
  contributor: "", // free text, e.g. "Councillor"
  notes: "",
  meta: {}         // open for future properties, e.g. meta.patternId and meta.role for five-shot coverage
}

// story
{
  schema: 1,
  medium: "video",
  title,
  mode: "build",   // reserved: "reference" for future Deconstruct mode (read-only logged broadcast)
  tracks: { picture: [], sound: [], editorial: [] },
  groups: { [groupId]: { anchorId } }  // a group existing means it is locked
}
```

`medium` selects a vocabulary set from `CONFIG.media`. Only `video` is implemented. The structure must allow `audio` (no picture track), `photo` and `slideshow` to be added later purely as new CONFIG entries. Do not implement them.

---

## 2. Vocabularies (CONFIG)

Each type has: `key, track, short, label, icon (inline SVG or emoji), colour, defaultLength, description`.

Colour is never the only differentiator. Every brick shows an icon, and a short label when it is wide enough (see 3).

**Picture:** WS, MS, MCU, CU, ECU, OTS, Detail, GV, Graphic, PTC.

**Sound:** Reporter track, SOT, Atmos, Natural sound, Music bed, Silence.

**Editorial:** each function has a `lens`. The three lenses are different kinds of thing and must not be flattened into one list:

- `argument`: context, claim, evidence, explanation, reaction, challenge, consequence, expertise
- `structure`: transition, open, close
- `pace`: breathe

Plus `unassigned` (no lens; see 1.4).

**Library compounds:** Interview SOT (MCU + SOT + unassigned span); PTC (PTC + Reporter sound + unassigned span). Both are created as a group.

Patterns may only use existing vocabulary keys.

---

## 3. Bricks: rendering

- Width = `length × var(--stud)`, with `--stud: 20px`. **Always the true width.** A brick is never drawn wider or narrower than its length.
- The studs come from the repeating one-stud middle sprite, so longer bricks gain studs automatically with no extra code. **The studs are the length indicator.** Do not show a number on the brick.
- Bricks under 3 studs show the icon only. Their label appears in a tooltip, in the inspector and in the aria-label.
- The resize handle is a thin strip on the right edge, so even 1-stud bricks keep a draggable surface.
- Realistic rendered plastic. Bricks and baseplate use pre-rendered sprites made by `tools/render-bricks.mjs` (a dependency-free ray-marcher run with Node; not part of the app). It renders neutral shade, specular and shadow maps for a left end, a one-stud middle and a right end (plus a one-stud brick and a baseplate tile). These are embedded in `index.html` as data URIs and tinted per brick with CSS blend modes. The ends sit over a middle that repeats once per stud, so studs stay exactly one grid unit wide at every length. No minifigures, logos or printed textures.
- Unassigned spans are grey with a dashed outline.
- Groups show a thin connector down the side across tracks, plus a lock icon. A drifted group shows a visible tear in the connector.
- Every brick has `tabindex="0"`, `role="button"` and an `aria-label` such as "MCU, 5 studs, grouped with SOT, claim". A screen-reader user has no other way to get the length, so it goes in the label even though it is not shown visually.
- The baseplate is a stud grid with a faint marker every 5 studs. There are **no numbers and no time ruler**. The baseplate extends past the longest track by a few studs, so there is always room to build.
- Horizontal scroll when needed. Never shrink studs until labels become unreadable.

---

## 4. Interaction

- **Library** below the baseplate, with tabs: Picture | Sound | Editorial | Compounds | Patterns. Each item has a drag handle **and** an "Add" button.
  - Single bricks: if the selected brick is in the same track, Add inserts directly after it; otherwise it appends to the end of the relevant track.
  - Compounds and multi-track patterns: Add follows the rules in 1.5.
- **SortableJS** handles dragging single bricks from the library into a track and reordering within a track. Use one Sortable group per track (no cross-track drags) and filter out the resize handle. Convert every drop into a MODEL operation. Never mutate the DOM directly as the source of truth.
- **interact.js** handles resizing by dragging a brick's right edge, snapping to a 1-stud grid, and dragging compounds and multi-track patterns onto the highlighted shared boundaries.
- If SortableJS and interact.js conflict on the same elements, report it at checkpoint 3 instead of hacking around it.
- **Selection:** click, Enter or Space selects a brick. Shift+click and Shift+Space add it to or remove it from a multi-selection.
- **Keyboard** (required, not optional). Single-key shortcuts only act when a brick has focus, never while typing in an inspector field.
  - Tab / Shift+Tab move focus to the next/previous brick in the track
  - ↑/↓ move focus to the brick directly above/below in the neighbouring track
  - ←/→ move the brick one place in the track
  - `[` / `]` shorten/lengthen by 1 stud
  - `D` duplicate, `Delete` or `Backspace` remove, `L` lock selection / unlock group, `R` realign drifted group
  - `Ctrl/Cmd+Z` undo, `Ctrl/Cmd+Shift+Z` redo
  - Show a small keyboard help panel listing all of the above.
- **Inspector** (selected block): type (switchable within its track, including unassigned for spans), length (a stepper labelled in studs), voice (sound only), contributor, notes, group status (drifted or aligned) with Realign and Unlock, duplicate, remove.
  - For editorial spans, the inspector also shows the picture and sound under the span, so the student can check the label against what is actually there.
  - For a multi-selection, the inspector offers Lock, or explains why the blocks can't be locked.
  - For a five-shot coverage brick, the inspector shows the "Show three edits" button (see 8).

---

## 5. Views

The **same DOM elements** are used in all four views. Blocks never change position between views. Only emphasis, labels and the insights lens change, via a class on the root element.

- **Build**: all three tracks compact, full labels.
- **Technical**: picture and sound foregrounded, editorial dimmed. Insights filtered to the `technical` lens.
- **Editorial**: editorial foregrounded. Picture and sound bricks show their technical label small and secondary. Insights filtered to `editorial`.
- **X-Ray**: the three tracks separate vertically in CSS 3D (a container with `perspective`, each track given a `translateY`/`translateZ` offset, animated at about 400ms), like an exploded brick construction. Draw faint vertical guide lines at every cut in any track, so it is obvious where picture cuts and sound doesn't (and the reverse). Overhangs (1.3) should be at their most visible here. Selection and focus must survive the view switch. Respect `prefers-reduced-motion`.

---

## 6. Package overview

There are no durations and no targets. The overview is about **shape and proportion**.

- **Track lengths:** one horizontal bar per track, all drawn to the same scale, so a script overhanging the pictures is obvious at a glance.
- **Sound composition** by voice (reporter, authority, affected, expert, vox, atmos/natural, music, silence), shown as proportions of the sound track, as a stacked bar plus %.
- **Editorial coverage:** the proportion of the picture track that has an assigned span (unassigned counts as uncovered), and the breakdown of assigned spans by lens.

---

## 7. Insights engine

Rules are data in `CONFIG.rules`:

```js
{ id, lens: "technical"|"editorial", kind: "notice"|"consider"|"question",
  test: story => null | { blockIds: [...], vars: {...} },
  message: vars => string }
```

The engine runs every rule after every state change and renders results in the Insights panel. Clicking an insight highlights the blocks it refers to.

**Tone:** there are no scores, percentages of "good", or words like *correct, wrong, error, must, fail*. Use *Notice…, Consider…, What happens if…, Compare…, Try moving…*

**Talk about proportion and relationship, never time.** For example: "twice as long as", "runs past the pictures", "the longest brick in the piece". Never "18 seconds".

**Editorial rules only ever see the student's own labels**, so they must question those labels rather than grade them. Students will otherwise learn to label things so that the warnings go away. Where it fits, phrase editorial insights as a question aimed at the label. For example:
- "You've labelled this span *evidence*. What does the viewer actually see or hear that proves it?"

Messages that name people use the `contributor` field and fall back to generic wording (e.g. "the authority voice") when it is empty.

Starter rules (about 12):

Technical

- the sound track runs past the end of the pictures, or the pictures run on with nothing underneath → "Notice your script is longer than the pictures it's written over. What would you cut, or what would you add to cover it?"
- no atmos or natural sound anywhere
- one reporter track brick is more than a third of the sound track
- the same framing appears in three consecutive picture blocks
- the first picture block is not a WS or GV (framed as a question, not a fault)
- one picture brick is much longer than the average (more than 2.5×)
- a group has drifted out of alignment → "Notice the councillor's words and picture no longer start together. Is that deliberate?"
- every SOT is grouped with an MCU → "Notice every interview is seen as a talking head. What would the viewer see if one of these voices ran over what they're describing?"

Editorial

- a claim span with no later span labelled *challenge* → "Nothing in the piece challenges this claim. Is it one that needs challenging?"
- authority voices get more than 1.5× the total length of affected voices → "Compare the councillor's brick with the resident's. Is that the balance you intend?"
- a large proportion of the picture track has no assigned editorial span
- a *consequence* span sits over a sound block with a reporter voice → "Whose consequence is this — yours or theirs?"

---

## 8. Patterns

Patterns are insertable sub-assemblies, like chords. The UI must say plainly: **"Starting structures, not rules. Insert, then pull apart."**

Each pattern declares which tracks it fills and sets an **explicit length for every brick**, so that any group inside it starts on a shared boundary. Multi-track patterns are inserted like compounds (1.5): only at a shared boundary, never drifted on arrival. Inserting a pattern is one undo step.

Lengths are in studs. \* marks a length that differs from the brick's default.

**1. Basic package body** (all tracks; five 10-stud segments). Editorial spans are left unassigned so the student does the labelling.

| Segment | Picture | Sound | Editorial |
|---|---|---|---|
| VO | WS 5 + CU 5\* | Reporter 10 | unassigned 10 |
| SOT | Interview SOT: MCU 10 | SOT 10 | unassigned 10 |
| VO | GV 5 + CU 5\* | Reporter 10 | unassigned 10 |
| SOT | Interview SOT: MCU 10 | SOT 10 | unassigned 10 |
| VO | WS 5 + GV 5 | Reporter 10 | unassigned 10 |

**2. Five-shot coverage** (picture only). Label it *coverage — what you need to shoot*, not an edit order. Inserted after the selected picture brick, else appended to the picture track.

CU 4 (notes: "action"), CU 4 ("face"), WS 5, OTS 4, Detail 4 ("creative angle").

The five bricks share `meta.patternId`. When one of them is selected, the inspector shows **"Show three edits of these five shots"**. Each press is one undo step and cycles through these orders (listed by the notes on each shot):

- *As shot:* CU action, CU face, WS, OTS, Detail
- *WS first:* WS, CU action, CU face, OTS, Detail
- *Action first:* CU action, WS, OTS, CU face, Detail
- *Detail first:* Detail, CU face, OTS, CU action, WS

Then it returns to as shot. If the student has reordered the shots into an order not on this list, the next press goes to as shot. The button is disabled, with a short note, once the five bricks are no longer consecutive in the track.

**3. Human-interest sequence** (all tracks). The editorial labels are the point of this pattern.

| Beat | Picture | Sound | Editorial |
|---|---|---|---|
| establish | WS 5 | Natural sound 5\* | context 5 |
| character | Interview SOT: MCU 10 | SOT 10 | unassigned 10 |
| action | MS 5 | Reporter 10 (under action and detail) | evidence 5 |
| detail | Detail 5\* | ↑ | breathe 5 |
| close | WS 5 | Natural sound 5\* | close 5 |

**4. Explainer** (all tracks; four 10-stud segments). The editorial labels are the point of this pattern.

| Beat | Picture | Sound | Editorial |
|---|---|---|---|
| explanation | GV 5 + MS 5 | Reporter 10 | explanation 10 |
| graphic/evidence | Graphic 6 + CU 4 | Reporter 10 | evidence 10 |
| expert | Interview SOT: MCU 10 | SOT 10, voice expert | expertise 10 |
| consequence | WS 5 + GV 5 | Reporter 10 | consequence 10 |

---

## 9. Example package: "Council housing: the backlog"

Load this on first run, with an obvious **Start empty** option. Show it as an illustration of the interface, not a model answer.

All values are in studs. Tracks are packed, so each `start` below is simply what the order produces; it is shown for checking only and is not stored.

Picture
| start | length | type | note |
|---|---|---|---|
| 0 | 6 | WS | estate exterior |
| 6 | 5 | CU | repair notice on door |
| 11 | 12 | MCU | councillor (group A) |
| 23 | 5 | CU | waiting-list figures on screen |
| 28 | 5 | WS | resident's street |
| 33 | 5 | MCU | resident (not grouped) |
| 38 | 5 | CU | damp on wall (resident SOT continues underneath) |
| 43 | 5 | Detail | child's bedroom |

Sound
| start | length | type | voice |
|---|---|---|---|
| 0 | 11 | Reporter | reporter |
| 11 | 12 | SOT | authority — Councillor (group A) |
| 23 | 10 | Reporter | reporter |
| 33 | 10 | SOT | affected — Resident |
| 43 | 9 | Reporter | reporter |

Editorial
| start | length | function |
|---|---|---|
| 0 | 6 | context |
| 6 | 5 | evidence |
| 11 | 12 | claim (group A) |
| 23 | 10 | explanation |
| 33 | 10 | consequence |
| 43 | 5 | transition |

Group A has `anchorId` set to its picture member.

The example is deliberately imperfect, so the tool has things to raise on first load:

- The resident's SOT runs across a picture cut, which shows unlocking.
- The councillor's claim is never challenged.
- **The final reporter track overhangs the pictures by 4 studs.** It is the writing-to-pictures problem made visible.
- There is no atmos or natural sound anywhere.

It does not need to trigger every rule.

---

## 10. Persistence

- Autosave the current story to `localStorage` on every change (debounced).
- Toolbar: New · Export JSON · Import JSON · Reset to example.
- Import validates everything before loading anything:
  - `schema` is 1 and `tracks` has exactly `picture`, `sound` and `editorial` arrays;
  - every block has a unique `id`, a `type` valid for its track and an integer `length` ≥ 1;
  - every `groupId` refers to an entry in `groups`, and every group has two or more members with at most one per track;
  - every `anchorId` refers to a member of its group.
- If a file is invalid, report it plainly and do not load a half-built story.

---

## 11. Build order

Work in this order. Steps 1–5 are the core product; spend your polish there. Stop and show me at each checkpoint.

1. CONFIG + a minimal MODEL (the operations in 1.6) + a small `index.html?test` self-test covering insert, move, resize, group resize, drift detection, realign (success and "can't"), shared-boundary detection and overhang detection. Keep it short; this is a safety net, not a test suite.
2. Baseplate + bricks rendered from the example package: studs, plastic look, overhang treatment, group connectors. **Checkpoint: does it look right?**
3. Adding bricks from the library, drag to reorder (SortableJS), edge-drag resize (interact.js), keyboard equivalents, undo. Make resize and drop feel good. **Report any SortableJS and interact.js conflicts here.**
4. Compounds: insert at shared boundaries (drag with highlighted drop points, and Add), lock, unlock (with a visible separation moment), drift and realign.
5. Views, especially X-Ray: explode and reassemble smoothly, with cut guide lines. **Checkpoint: is the core delightful?**
6. Inspector.
7. Overview + insights engine + starter rules.
8. Patterns + Start empty + persistence and JSON import/export.
9. Accessibility pass (keyboard only, screen reader labels, contrast, reduced motion) and a narrow-screen pass (tracks scroll horizontally; inspector and insights stack underneath). **Checkpoint.**

If anything in this brief turns out to be contradictory or impractical in implementation, stop and ask. Do not quietly pick an interpretation. In particular, do not reintroduce seconds, durations or time targets anywhere in the UI.
