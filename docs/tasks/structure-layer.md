# Task: turn the Editorial layer into a Structure layer built on story beats

Read `CLAUDE.md`, `docs/decisions.md`, `docs/notice-principles.md` and `docs/traits.md` before starting. Everything below must respect them: one self-contained HTML file, Notice rules read traits (never brick codes), no time anywhere, no judgement, and saved work must keep opening.

## Why

The top layer currently holds argument labels (claim, evidence, consequence…). The course teaches package structure as **beats**:

- **Basic structure:** a thing is happening that we think is news → it's happening because of a thing, place or person, and it affects a thing, place or person (maybe you) → here's a person to explain that.
- **Extended structure:** the basic three, then a **pivot, AND or BUT**, where the story moves on → here's a related thing that gives more context, illustrates a core point, develops a theme or challenges the view → here's a person to explain that → here's what it all means and what might happen next.

The layer should lean into that structure. More play, less say: no typing, no planning forms.

## Decisions already made (don't reopen)

- **Studs only.** No seconds, no words-per-second, no "50 second" or "90 second" labels anywhere. Starting structures are "Basic" and "With a pivot", in relative studs.
- **Keep a PERSON beat** even though it overlaps the SOT or CLIP below it. The overlap is deliberate: the beat is the editorial role, the sound brick is how it's delivered, and a rule checks the gap between them.
- **No "Why now / Who cares / How do we tell it" card** and no summary-script field.
- **Rename the layer to Structure.** Display name `Structure`, blurb `How the story is built`. **The internal key stays `editorial`**, so storage, exports and imports keep working.
- **No rule prescribes a sequence of beats.** The structure is a scaffold, not a template. Rules may look at what comes after a pivot (that's a relationship in the build), but none may expect beats in a set order.

## 1. Bricks on the structure layer

Replace the brick-box contents of the top layer with these, in this order (both media):

| Code | Label on brick | Name | Default studs | Colour | Description (brick box info card) | Traits |
|---|---|---|---|---|---|---|
| NEWS | NEWS | A thing is happening | 8 | setup | A thing is, or was, happening that we think is news. Why now? | beat-news |
| BECAUSE | BECAUSE | Because… | 8 | setup | It's happening because of a thing, place or person, and it affects a thing, place or person. Maybe you. Who cares? | beat-because |
| PERSON | PERSON | A person explains | 10 | setup | Here's a person to explain that. | beat-person |
| AND | AND | AND | 2 | pivot-and | The pivot: the story widens. Here's something related to that. | pivot |
| BUT | BUT | BUT | 2 | pivot-but | The pivot: the story turns. Here's something that pulls the other way. | pivot |
| MORE | CONTEXT | More context | 8 | second | A related thing that gives more context. | beat-more |
| ILLUS | ILLUSTRATE | Illustrates it | 8 | second | A related thing that illustrates a core point. | beat-more |
| DEVELOP | DEVELOP | Develops a theme | 8 | second | A related thing that develops a theme. | beat-more |
| CHALLENGE | CHALLENGE | Challenges it | 8 | second | A related thing that challenges the view. | beat-more challenge |
| NEXT | NEXT | What next | 6 | ending | What all of that means, and what might happen next. | beat-next |
| BREATHE | BREATHE | Breathe | 5 | pink (darkened, below) | A pause to let something land. | (none) |
| UNSET | ? | Not decided yet | 5 | grey, dashed (existing) | A span you haven't decided on yet. | unlabelled |

`beat-news`, `beat-because` and `beat-more` aren't read by any rule yet. They're there so future rules don't need new traits; say so in `traits.md`.

**Colours.** Add to `PAL` (top / front / end, then ink). The aim is that the pivot visibly splits the wall. Every label must reach 4.5:1 against its front colour (`docs/accessibility.md`, item 4); these have been checked:

- `setup`: the existing purple, `#A274DB` / `#7440B0` / `#552E85`, white ink (6.8:1)
- `pivot-and`: cyan, `#7FE3F0` / `#1FA0B3` / `#157A89`, ink `#06262B` (5.1:1)
- `pivot-but`: coral, `#FF9A85` / `#CD3D26` / `#A33521`, white ink (4.9:1; the first draft's `#D9472F` was 4.3:1)
- `second`: indigo, `#8C9CF2` / `#4A5BC7` / `#34409A`, white ink (5.8:1)
- `ending`: dark violet, `#7B6A9A` / `#43345F` / `#2B2140`, white ink (11.1:1)
- `pink` (BREATHE): front darkened from `#C95388` (4.1:1) to `#C4427C` (4.75:1)

**Retired bricks:** CLAIM, EVIDENCE, CONSEQ, EXPLAIN **and CONTEXT** leave the brick box but **stay in `BRICK_ROWS`**, so older saves and exports still open and draw. Add a `RETIRED` set that the palette filters out. CLAIM keeps its `claim` trait; the others have none. Old CONTEXT meant "what the viewer needs to know first" and usually sits at the start of a build, so the new second-half beat gets a new code, `MORE`, rather than changing what old work shows. CHALLENGE keeps its code: its old and new meanings are close.

**Key and wording:** the layer key's representative brick for this layer becomes `NEWS` in both media. In `MEDIA`, the "How it works" text says "with the story's structure on top" instead of "meaning on top". Anywhere else that calls this layer "meaning" or "editorial" in text a student reads becomes "structure".

## 2. Starting structures

Add a `STRUCTURES` config and a small row of buttons in the brick box under the Structure heading: **Starting structure: [Basic] [With a pivot]**.

- **Basic:** NEWS 8, BECAUSE 10, PERSON 10
- **With a pivot:** NEWS 8, BECAUSE 8, PERSON 10, AND 2, UNSET 8, PERSON 10, NEXT 6. The second-half beat is left as `?` so the student chooses the flavour.

Pressing one **replaces only the structure layer** (the other layers stay as they are) and is one undo step. It says:

- video: "Laid a basic structure. Now build the pictures and sound underneath it. Undo takes it back." / "Laid a structure with a pivot. Now build the pictures and sound underneath it. Undo takes it back."
- audio: the same, with "the sound and script" in place of "the pictures and sound".

Hovering or focusing a button shows the beats in the info card, e.g. "A thing is happening → Because… → A person explains." Lengths are studs; never mention time.

Also update the empty-stage message in both media to point at this: title **"Start with the story"**, text along the lines of "Lay a starting structure from the brick box, or put down some shots (audio: the sound of the story) and build up. Then watch where the layers don't line up."

## 3. Examples from the lectures

Replace the council-housing examples. Keep OOV/SOT and Cue + clip. Each example is laid end to end; `['GAP', n]` leaves n empty studs. Each has a deliberate imperfection for students to find. Keep header button labels short: the video header will hold three examples, so check it at 1280px wide.

**Video: "Sea Life"** (button `Sea Life`; name `Basic package: Sea Life stocktake`; the basic structure, no pivot. Imperfection: three mid shots cut straight into each other.)
- picture: GV 4, WS 6, MS 4, MS 4, MS 4, MCU 10
- sound: NAT 10, ATM 12, SOT 10
- script: VO 22, RUN 10
- structure: NEWS 10, BECAUSE 12, PERSON 10

**Video: "Pumpkins"** (button `Pumpkins`; name `Package with a pivot: small pumpkins`. Imperfection: the last line runs past the pictures.)
- picture: WS 4, CU 4, GV 4, CU 4, MCU 10, WS 5, DET 5, MCU 10, WS 6
- sound: ATM 16, SOT 10, NAT 10, SOT 10, ATM 6
- script: VO 16, RUN 10, VO 10, RUN 10, VO 8
- structure: NEWS 8, BECAUSE 8, PERSON 10, AND 2, DEVELOP 8, PERSON 10, NEXT 6

**Video: OOV/SOT** (keep as is, but change its structure to): NEWS 6, BECAUSE 14, PERSON 10, UNSET 4

**Audio: "Pumpkins"** (button `Pumpkins`; name `Radio package with a pivot: small pumpkins`. Imperfection: ends on a dry sign-off.)
- sound: GAP 4, ACT 6, ATM 6, CLIP 10, ACT 10, CLIP 10, ATM 6
- script: CUE 4, TRK 12, RUN 10, TRK 10, RUN 10, TRK 6, SIGN 3
- structure: NEWS 8, BECAUSE 8, PERSON 10, AND 2, DEVELOP 8, PERSON 10, NEXT 6

**Audio: Cue + clip** (keep, but change its structure to): NEWS 8, PERSON 12, UNSET 4

The example message stays "Someone built this. Explore it: what do you notice? Then press Notice."

## 4. Notice rules

Add to `TRAITS` and document in the vocabulary comment: `beat-news`, `beat-because`, `beat-person`, `pivot`, `beat-more`, `beat-next` (plus the existing `challenge`, `unlabelled` and `claim`).

Add these rules to `NOTICE_RULES`, in the same style as the existing ones: traits only; measured in studs; messages state only what the build shows; `spans`, `layers` and `bricks` filled so the highlight works; no stud numbers.

| id | Type | Fires when | Message (adapt wording, keep the tone) |
|---|---|---|---|
| `who-explains` | Look | A `beat-person` brick has **no** `voice` brick under any of its studs in the sound layer, **and** the `whose-voice` rule isn't already reporting the same stretch (a `no-words` brick in the script under it with no voice) | "This says a person explains it, but nothing in the sound layer underneath is a voice. Who is speaking?" |
| `no-pivot` | Question | Two `beat-person` bricks next to each other on the structure layer (no other `beat-person` between them) have no `pivot` brick between the end of the first and the start of the second. Check each such pair; report the first. **Only `beat-person` bricks count**: no fallback to voice bricks, so a student who hasn't used the structure layer never sees it. Highlight both PERSON bricks (the stretch between them can be empty when they touch). | "Two people explain, with no AND or BUT between them. What moves the story from one to the other?" |
| `after-the-turn` | Question | For some `pivot` brick, no `voice` brick in the sound layer **starts** at or after it. Check each pivot; report the first. | "After the AND, no new voice starts in the sound layer. Who could speak to the second part?" (use the pivot's own label, AND or BUT) |
| `where-it-ends` | Question | A `pivot` brick exists and no `beat-next` brick starts after the (last) pivot | "The structure turns at the AND, but there's no NEXT after it. What does it all mean, and what happens next?" |

- **Only fire `where-it-ends` when there's a pivot.** The basic structure legitimately ends on the person. Because it looks for NEXT anywhere after the pivot, a NEXT followed by BREATHE or `?` doesn't trigger it.
- **Keep the existing `claim` rule.** It now only affects older work with CLAIM bricks. Change only its wording: "in the meaning layer" becomes "in the structure layer" (also in `notice-principles.md`, which quotes it).
- **Don't add a rule that expects a challenge after every BECAUSE.** Whether a story needs one is the student's call, and BUT and CHALLENGE are there for them to choose.
- **No rule may prescribe a sequence of beats.**

## 5. Docs, fixtures and tests (same change)

- **`docs/traits.md`:** the Structure layer table, the new traits (noting which no rule reads yet), the four new rules, and a note on retired bricks.
- **`docs/decisions.md`:** update the "Four video layers" row (editorial → structure) and add rows for: the Structure layer (lecture beats; key stays `editorial`); starting structures replacing only the top layer; retired bricks, including why CONTEXT became MORE; no rule prescribes a sequence; `where-it-ends` only with a pivot; `no-pivot` reads PERSON beats only.
- **`CLAUDE.md`:** the opening description ("editorial meaning") and anything else that names the layer.
- **Fixtures:** add one per new rule, with `_about` lines:
  - PERSON over ATM (`who-explains`);
  - two PERSON beats and no pivot (`no-pivot`);
  - a pivot with no new voice after it (`after-the-turn`);
  - a pivot, ending on DEVELOP (`where-it-ends`);
  - a pivot, then NEXT, then BREATHE (`where-it-ends` doesn't fire);
  - the basic structure ending on PERSON (none of the four fire);
  - PERSON over a RUN with no voice under it (`whose-voice` only, not `who-explains` as well).

  Add exports of the new examples. **Keep** the existing example fixtures: they're now tests that older work with retired bricks still opens.
- **`fixtures/expected.json`:** add the new entries. For existing fixtures whose notices change, check the change is intended before editing each line by hand. Don't regenerate the file.
- **Tests** that load the old example keys (`pkg`, `rpkg`) move to the new ones.
- **Run** `python tests/run_tests.py` and `python tests/a11y_check.py`. Then take screenshots of both new examples and of each starting structure laid over an empty build, and look at them. Check that the pivot visibly splits the wall and the labels are readable, and that the header fits at 1280px.

## Done when

- The brick box's top section reads **Structure: How the story is built**, with the two starting-structure buttons and the twelve beat bricks.
- Both starting structures lay correctly, are one undo each, and leave the lower layers alone.
- The Sea Life and Pumpkins examples load in video, and Pumpkins in audio, each producing the expected notices.
- An older save or export containing CLAIM, EVIDENCE, CONSEQ, EXPLAIN or CONTEXT still opens and draws.
- All tests pass, the accessibility check shows no *new* violations, and nothing mentions seconds except the existing line saying studs are *not* seconds.

## Changes from the first draft (after review, 30 September 2026)

1. `no-pivot` reads PERSON beats only; the voice-brick fallback would have fired on every two-interview build.
2. `where-it-ends` looks for NEXT anywhere after the pivot, so a trailing BREATHE or `?` doesn't trigger it.
3. `after-the-turn` says "no new voice starts", which stays true when a voice runs across the pivot; each pivot is checked.
4. Sea Life gets an imperfection (three mid shots in a row); the first draft produced no notices at all.
5. Coral and BREATHE pink darkened to pass 4.5:1.
6. CONTEXT retired; the new beat is `MORE` (label still CONTEXT), so old work keeps its meaning.
7. `who-explains` skips stretches `whose-voice` already reports.
8. Short example button labels; header checked at 1280px.
9. The `claim` message says "structure layer"; audio wording for starting structures; the "no seconds" check excludes the "not seconds" line; `CLAUDE.md` and `decisions.md` row 9 added to the docs list.
10. The "no order" decision reworded to "no rule prescribes a sequence of beats".
