# StoryBlocks: bricks, traits and Notice rules

The Notice rules never look at brick names. They only read each brick's **traits**, so changing the bricks means changing traits, not code.

A brick is its layer, its medium (video, audio or both) and a few plain-word traits. A rule measures where bricks with certain traits sit and how many studs they share. It reports only lengths, the bricks involved, and "at the start" or "at the end". A brick with no traits is ignored by every rule except the two that check whether a layer has anything in it at all.

All of this lives in the `TRAITS` table in `storyblocks.html`, directly under the brick list. **Keep this file in step with it.**

## Picture bricks

Video only. Every shot belongs to one size family; studio and reporter shots also say who is on screen.

| Brick | Name | Traits | Read by |
|---|---|---|---|
| WS | Wide shot | wide | Shot sizes |
| GV | General view | wide | Shot sizes |
| MS | Mid shot | mid | Shot sizes |
| MCU | Mid close-up | mid | Shot sizes |
| CU | Close-up | close | Shot sizes |
| DET | Detail | close | Shot sizes |
| GFX | Graphic | graphic | nothing yet |
| PTC | Piece to camera | mid, reporter | Shot sizes; In or out of vision? |
| inVIZ (code `INVIZ`) | Presenter in vision | mid, presenter | Shot sizes; In or out of vision? |
| WALL | Studio screen | wide, presenter | Shot sizes; In or out of vision? |

## Sound bricks

Everything the audience hears except the script. Any sound brick, whatever its traits, counts as "something to hear" for Nothing to hear.

| Brick | Name | Medium | Traits | Read by |
|---|---|---|---|---|
| SOT | Interview (sync) | Video | voice | Two voices; Whose voice? |
| CLIP | Interview clip | Audio | voice | Two voices; Whose voice? |
| VOX | Vox pops | Both | voice, repeat-mid | Two voices; Whose voice?; Shot sizes (exemption) |
| NAT | Natural sound | Video | place | The place itself |
| ACT | Actuality | Audio | place | The place itself |
| ATM | Atmos | Both | place | The place itself |
| MUS | Music bed | Both | music | nothing yet |
| SIL | Silence | Both | silence | nothing yet (fills the layer, so it quietens Nothing to hear) |

## Script bricks

What is read out, who reads it, and (video only) whether the reader should be on screen. Presenter bricks are dark red on the board, reporter bricks red.

| Brick | Name | Medium | Traits | Read by |
|---|---|---|---|---|
| CUE | Presenter cue | Both | words, presenter, inviz | Writing to pictures; Two voices; In or out of vision? |
| OOV | Presenter OOV | Video | words, presenter, oov | Writing to pictures; Two voices; In or out of vision?; The place itself |
| BACK | Back-anno | Both | words, presenter, inviz | Writing to pictures; Two voices; In or out of vision? |
| VO | Voiceover | Video | words, reporter, oov | Writing to pictures; Two voices; In or out of vision?; The place itself |
| PTC (code `PTCW`) | PTC words | Video | words, reporter, inviz | Writing to pictures; Two voices; In or out of vision? |
| TRK | Reporter track | Audio | words, reporter | Two voices; The place itself |
| PTM | Piece to mic | Audio | words, reporter | Two voices; The place itself |
| LINK | Link | Both | words, reporter | Writing to pictures; Two voices; The place itself (audio only) |
| SIGN | Sign-off | Both | words, reporter | Writing to pictures; Two voices; The place itself (audio only) |
| RUN | Clip runs | Both | no-words | Whose voice? |

## Structure bricks

Both media. The story's beats, from the lectures: the basic structure (NEWS, BECAUSE, PERSON), then a pivot (AND or BUT), a related second-half beat, another PERSON, and NEXT. The layer's internal key is still `editorial`, so saves and exports keep working.

| Brick | Label | Name | Colour | Traits | Read by |
|---|---|---|---|---|---|
| NEWS | NEWS | A thing is happening | purple | beat-news | nothing yet |
| BECAUSE | BECAUSE | Because… | purple | beat-because | nothing yet |
| PERSON | PERSON | A person explains | purple | beat-person | Who explains?; One person to the next |
| AND | AND | AND | cyan | pivot | One person to the next; After the turn; Where it ends |
| BUT | BUT | BUT | coral | pivot | One person to the next; After the turn; Where it ends |
| MORE | CONTEXT | More context | indigo | beat-more | nothing yet |
| ILLUS | ILLUSTRATE | Illustrates it | indigo | beat-more | nothing yet |
| DEVELOP | DEVELOP | Develops a theme | indigo | beat-more | nothing yet |
| CHALLENGE | CHALLENGE | Challenges it | indigo | beat-more, challenge | Claim |
| NEXT | NEXT | What next | dark violet | beat-next | Where it ends |
| BREATHE | BREATHE | Breathe | pink | none | nothing |
| UNSET | ? | Not decided yet | grey, dashed | unlabelled | nothing yet |

**Retired bricks.** CONTEXT, CLAIM, EVIDENCE, CONSEQ and EXPLAIN are no longer in the brick box (the `RETIRED` set), but stay in `BRICK_ROWS` so older saves and exports open and draw. CLAIM keeps its `claim` trait, so the Claim rule still works on older work; the others have none. The new "More context" beat has the code `MORE`, not `CONTEXT`: old CONTEXT meant "what the viewer needs to know first", so reusing the code would have changed what older work shows.

## Trait vocabulary

| Trait | Layer | Means | Used by |
|---|---|---|---|
| wide, mid, close | Picture | The shot-size family | Shot sizes |
| presenter | Picture, script | The presenter is on screen (picture) or reads it (script) | In or out of vision? |
| reporter | Picture, script | The reporter is on screen (picture) or reads it (script) | In or out of vision?; The place itself (audio) |
| graphic | Picture | Made-up pictures: data, maps, quotes | unused |
| voice | Sound | Someone speaking: interview, vox | Two voices; Whose voice? |
| place | Sound | The sound of the place: natural sound, actuality, atmos | The place itself |
| repeat-wide, repeat-mid, repeat-close | Sound | Shots of that size cut together under this sound are the convention | Shot sizes (exemption) |
| music | Sound | A music bed | unused |
| silence | Sound | Deliberate quiet | unused (but it fills the layer) |
| words | Script | Something is read out | Writing to pictures; Two voices; The place itself |
| inviz | Script | Read on screen: the reader should be in the picture below | In or out of vision? |
| oov | Script | Read over pictures, reader not on screen | In or out of vision?; The place itself (video) |
| no-words | Script | Nothing read: a clip carries it | Whose voice? |
| beat-person | Structure | A person explains | Who explains?; One person to the next |
| pivot | Structure | AND or BUT: where the story moves on | One person to the next; After the turn; Where it ends |
| beat-next | Structure | What it all means, what happens next | Where it ends |
| beat-news, beat-because, beat-more | Structure | The other beats | unused (there so future rules don't need new traits) |
| claim, challenge | Structure | Claim (retired, older work) and Challenges it | Claim |
| unlabelled | Structure | A span not yet decided | unused |

## The Notice rules

Thirteen rules. "Look" rules state a measurable relationship; "Question" rules read the student's labels or a whole layer and only ask. Notice shows up to three: Look before Question, each group left to right along the build.

| Rule (id) | Type | Medium | Fires when | Reads |
|---|---|---|---|---|
| Writing to pictures (`words-past-pictures`) | Look | Video | Script words run on after the last picture | words |
| Nothing to see (`nothing-to-see`) | Look | Video | Sound or script over a gap in the pictures, or sound running on after the last picture | whether each layer is filled |
| Nothing to hear (`nothing-to-hear`) | Look | Both | Video: a picture with nothing in sound or script above it. Audio: a stretch with nothing in sound or script | whether each layer is filled |
| Two voices (`two-voices`) | Look | Both | Script words overlap a voice in the sound layer | words, voice |
| Whose voice? (`whose-voice`) | Look | Both | Part or all of a RUN has no voice under it | no-words, voice |
| In or out of vision? (`in-or-out`) | Look | Video | On-screen words over pictures that aren't the reader, or out-of-vision words over pictures that are | inviz, oov, presenter, reporter |
| Shot sizes (`shot-sizes`) | Look | Video | Three shots of one size family cut straight into each other, unless each sits mostly under a matching repeat-* sound | wide, mid, close, repeat-* |
| The place itself (`the-place`) | Question | Both | No sound brick is place sound; or voice-over has nothing under it (video: oov words; audio: reporter words) | place, words, oov, reporter |
| Who explains? (`who-explains`) | Look | Both | A PERSON beat has no voice under any of its studs, unless a RUN sits under it (Whose voice? already says so) | beat-person, voice, no-words |
| One person to the next (`no-pivot`) | Question | Both | Two PERSON beats in a row with no pivot starting between them. PERSON beats only, never voice bricks, so a build without them never sees it | beat-person, pivot |
| After the turn (`after-the-turn`) | Question | Both | No voice in the sound layer starts at or after a pivot | pivot, voice |
| Where it ends (`where-it-ends`) | Question | Both | There's a pivot and no NEXT starts after the last one. Never without a pivot: the basic structure ends on the person | pivot, beat-next |
| Claim (`claim`) | Question | Both | Nothing labelled challenge starts after a claim ends (older work only: CLAIM is retired) | claim, challenge |

## Worth checking

- **Seven traits have no rule yet:** graphic, music, silence, unlabelled, beat-news, beat-because and beat-more. BREATHE and four retired bricks carry no traits at all.
- **No rule prescribes a sequence of beats.** The structure rules look at what's under a PERSON beat, what lies between two of them, and what comes after a pivot.
- **LINK and SIGN are neither on screen nor out of vision,** so In or out of vision? ignores them. A sign-off over the wrong picture will never be noticed.
- **CUE is always on screen.** A presenter reading over pictures should use OOV; if students use CUE instead, the tool asks "which is it?".
- **Radio bricks carry no on-screen or out-of-vision traits,** because there are no pictures to check them against.
- **Music is not place sound.** A music bed under a voice-over still raises The place itself. *(Open question.)*
- **"mid" covers MS as well as MCU.** Three MSes under a vox pop also pass quietly. *(Open question.)*
- **A SIL brick is the student's way of saying "that silence is meant":** it fills the sound layer, so Nothing to hear stays quiet over it.
