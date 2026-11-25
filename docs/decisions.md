# Design decisions

Decisions already made, with the reason. Reverse one only deliberately, and record the change here.

| Decision | Why |
|---|---|
| **Isometric look, not a flat timeline.** | Tried a flat front-on timeline (`archive/journalism-blocks.html`); it lost the feel. Long stories are handled with Fit and zoom instead. |
| **Relative length (studs), never time.** | What matters is how long things are against each other, not seconds. |
| **Four video layers: picture, sound, editorial, structure.** Three for audio (no picture). | Editorial holds everyone who speaks (script, interviews, vox pops); sound holds the place under them. Words were split from sound so they aren't laid down twice. |
| **Presenter and reporter words both live in Editorial**, in different colours. No separate presenter-audio brick. | Same reason: no double entry. The sound under an in-vision presenter is silence or natural sound. |
| **Two audio rows: Editorial (who speaks) over Sound (the place).** Interviews and vox pops sit on the Editorial layer with the script; NAT, atmos, music and silence sit underneath. Still no mix levels. | Replaced "No multitrack mixing" (Nov 2026): the editorial voice of a piece and its natural sound are separate decisions, and NAT under a voiceover had nowhere to go. Mix levels stay out: finishing detail. |
| **RUN, Two voices and Whose voice? retired** with that change. | A clip now sits on the Editorial layer itself, so RUN isn't needed. Words and an interview can't overlap on one layer: the bricks shove instead of Notice pointing it out. Accepted. |
| **Older builds are converted as they open, simply.** Saves move from `storystack.v4.` to `storystack.v5.`; v4 is never overwritten. | Old builds weren't a priority; a clash between words and an interview is resolved by shoving the later brick along. |
| **Cutaways need no special handling.** | Layers are what the audience gets, not what was recorded. A cutaway's own sound isn't heard, so a CU over a running SOT is correct. |
| **Free placement with gaps; bricks shove their touching neighbours.** | Physical, LEGO-like behaviour. A gap absorbs a shove. Removing leaves a gap. Chosen over strict "no room, no drop". |
| **No transparent "gap" brick.** | Empty space *is* the gap. |
| **A SIL brick means "this silence is meant".** | It fills the sound layer, so Nothing to hear stays quiet over it. It's the student's way of saying "deliberate" through the bricks. |
| **No selected-brick panel.** A small translucent toolbar floats above the selected brick instead. | Play and exploration first; the stage gets the full width. |
| **The brick box is a drawer** that can close to a thin strip. | Less clutter. |
| **The running order is for screen readers only**: hidden on screen, plain text (no buttons), under a "Running order" heading. | A visible list added little for sighted students; the bricks already show it. No buttons, because hidden controls would take keyboard focus out of sight. |
| **The layer key is fixed bottom-left** and doubles as a solo control. | Floating labels overlapped the board. The bottom-left corner is always empty in isometric. Solo fades higher layers and makes them click-through. |
| **Faded bricks don't catch clicks.** | The brick you can see through the fade is the one you get. |
| **View can turn ±20° and tilt ±15°. No roll** (removed Nov 2026). | Beyond that the drawing order and visible faces stop being correct. Roll only spun the flat picture, which looked distorted. |
| **The build keeps its size while it's turned.** The stage fits to the isometric view; at Fit a turned build may run past the edges until it's turned back. | Refitting on every frame of a turn made the model shrink and grow, which read as wobble. |
| **Labels are printed on the brick face**: baseline along the bottom edge, letters upright, never stretched. Studs are the true projection of a circle at any angle. | Slanted, stretched labels and studs that didn't lean with the view made the turned model look distorted. |
| **Drag follows horizontal pointer movement only.** | Projecting onto the diagonal axis felt laggy, especially dragging left. |
| **A dragged brick is held and follows the pointer smoothly**, with a dashed outline where it will land; shoved bricks slide, and it settles into place on release. Landing in a brick's first half goes in front of it (shoving it along); in its second half, after it. | Jumping a whole stud at a time, and always landing after a brick, felt clunky. Clicks and the toolbar still use the plain "goes after" rule. |
| **Plain Notice first; no "that's deliberate" flag or reason capture yet.** | Avoid anything that feels like marking. See how students use it before adding flags or a "since last time" line. |
| **No notice without a relationship in *this* build.** | Generic "Evidence" and "Meaning" prompts were dropped as margin-comment nags. |
| **Vox pop MCUs aren't "repeated shots".** | `repeat-mid` on VOX: a string of MCUs is the grammar of a vox pop. |
| **"mid" covers MS and MCU.** | Open question: giving MCU its own size would make MS→MCU count as a change of size everywhere. |
| **Music is not place sound.** | Open question (see comment in `traits.md`): a music bed under voice-over still raises The place itself. |
| **Name: StoryBlocks.** | Note that Storyblocks is also a stock-media company; fine for internal teaching, worth revisiting before publishing or funding bids. Storage keys keep the old `storystack.` prefix. |
| **The top layer is Structure, built on the lecture beats** (NEWS, BECAUSE, PERSON; AND or BUT; a second-half beat; PERSON; NEXT). Its internal key stays `editorial`. | It replaced argument labels (claim, evidence…) so the layer matches how the course teaches package structure. Keeping the key means saves, exports and imports keep working. |
| **No built-in examples.** The board opens empty. | Students found them confusing; they should build and develop their own. The lecture builds (Sea Life, Pumpkins, OOV/SOT) live on as fixtures and can be shared as files. |
| **Starting structures replace only the structure layer**, as one undo step. | A scaffold to build under, without touching the student's pictures, sound or script. |
| **Retired bricks stay in the code** (CONTEXT, CLAIM, EVIDENCE, CONSEQ, EXPLAIN), just not in the brick box. The new "More context" beat is `MORE`, not `CONTEXT`. | Older work must still open. Reusing CONTEXT would have changed what older builds show (it meant "what the viewer needs to know first"). |
| **No rule prescribes a sequence of beats.** Rules may look at what comes after a pivot. | The structure is a scaffold, not a template. |
| **Where it ends only fires when there's a pivot**, and looks for NEXT anywhere after it. | The basic structure legitimately ends on the person; a NEXT followed by BREATHE or ? is fine. |
| **One person to the next reads PERSON beats only**, never voice bricks. | Falling back to voices would fire on every two-interview build, even one that never used the structure layer. |
| **IV renamed inVIZ** (code `INVIZ`; script trait `inviz`). | House terminology. Old saves and exports are translated via `CODE_ALIASES`. |
| **GV, DET, WALL, BACK, LINK and SIGN taken out of the brick box** (Nov 2026). | A smaller box. Retired, not deleted: they keep their traits so older work and the lecture fixtures still open and behave the same. |
