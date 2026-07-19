"""
Seed script for the `exercise` table, derived from the exercise index of
Steven Low's "Overcoming Gravity" 2nd Edition (chapters 24-27), per the
raw index text in ../../prompt_seed_exercises.md.

Inserts via raw SQL (psycopg2), not the SQLAlchemy ORM -- this is the
deliberate test case for the server_default=gen_random_uuid() added to
every UUID PK (see CLAUDE.md section 6): a bulk-load path that never
touches the ORM still has to get a valid id for each row, and this script
proves it does, without ever setting `id` itself.

*** DO NOT RUN THIS YET -- pending your review of the corrections below ***

1. RESOLVED -- exercise.name unique-constraint collisions: two exercise
   names appeared twice in the book's own index under different
   progression lines. Renamed to disambiguate rather than dropping either
   (same physical exercise, two contexts):
   - "Bar Pull-ups" in the Explosive Pull-ups line (Level 3, p.438) ->
     "Bar Pull-ups (Explosive)". The Pull-ups line version (p.425) keeps
     the original name.
   - "Butterfly Mount" in the Muscle-ups line (Level 15, p.536) ->
     "Butterfly Mount (Muscle-ups)". The Iron Cross line version (p.455)
     keeps the original name.

2. RESOLVED -- (progression_line, level) unique-constraint collisions:
   the book itself assigns the same level to two different exercises
   within one progression_line, twice. This is genuine book structure,
   not a data error, so rather than fudging a level number, the
   `exercise` model now has a nullable `level_variant` column ('a'/'b')
   and the unique constraint is (progression_line, level, level_variant)
   -- see app/models/exercise.py and migration df3166695497.
   - "Planche" line, Level 16: "Rings Straight-Arm, Straight-Body Press
     to Handstand" (p.470) -> level_variant='a'; "Rings Straight-Arm,
     Straight-Body from Planche to Handstand" (p.471) -> level_variant='b'.
   - "Muscle-ups and Inverted Muscle-ups" line, Level 8: "Straddle Front
     Lever to Muscle-up to Advanced Tuck Planche" (p.530) ->
     level_variant='a'; "L-Sit Muscle-up" (p.531) -> level_variant='b'.
   That same migration also makes `level` nullable -- a pre-existing
   mismatch (the model had it NOT NULL) that this seed data's "N/A"
   entries need regardless of the level_variant work.

3. RESOLVED -- movement_pattern for four Chapter 25 sub-sections was
   changed from "Pull" to "Static": L-Sit / Straddle-L / V-Sits / Manna,
   Back Lever, Front Lever, Front Lever Rows. The original blanket
   "Chapter 25 -> Pull" rule was applied literally to these, but they're
   isometric holds and Chapter 27's instructions treat the analogous
   categories (L-Sit/Front Lever/Back Lever/Elbow Levers/Flags) as
   "Static" -- the blanket per-chapter rule didn't match the source
   material for these four lines specifically.

4. REMOVED -- two rows dropped entirely as prose guidance headings, not
   discrete loggable exercises: "Training Toward the V-Sit and Manna"
   (p.385) and "The Plank Position" (p.545).

5. REMAINING JUDGMENT-CALL DERIVATIONS still worth double-checking
   (marked "# JUDGMENT:" inline, summarized here):
   - Equipment for the L-Sit/Straddle-L/V-Sits/Manna line is "Floor"
     rather than the chapter's "Bar" default, since L-sits are a
     parallette/floor hold, not a bar-hang exercise.
   - Equipment for Back Lever, Front Lever, and Front Lever Rows
     defaulted to "Bar" (no equipment named in the book's index text for
     these), even though these are also commonly trained on rings.
   - "Rope Climb Front Lever Rows" got equipment="Bar" by the same
     default, though it's actually rope-based -- there's no "Rope" value
     in the equipment set documented in app/models/exercise.py.
   - Rowing section's last two entries ("Straddle One-Arm Rows", "One-Arm
     Rows") and the entire Iron Cross section got equipment="Rings" by
     section context (Iron Cross is physically impossible on a bar; the
     Rowing section's other 5 entries are explicitly "Ring Rows"), even
     though the exercise names themselves don't say "Rings".
   - The four One-Arm Chin-up progressions were set to "Bar" (not
     "Rings"), disambiguating them from the "Rings" pull-ups earlier in
     the same combined progression_line ("Ring Pull-ups + One-Arm
     Chin-ups") -- one-arm chin-ups are a bar-based progression in the
     book, sharing a progression_line name with a separate ring
     progression only because the book groups them together.
   - "Rings Bent-Arm Press to Handstands" sub-section: two entries with
     no literal "Rings" in the name ("Chair Handstand", "Illusion Chair
     Handstand") got equipment="Rings" from the sub-section header.
   - "Dips" sub-section: three entries with no literal "Parallel Bar" in
     the name ("L-Sit Dips", "45-Degree Forward-Lean Dips", "One-Arm
     Dip") got equipment="Parallel Bars" from the sub-section header
     (contrasted with the book's separate "Rings Dips" sub-section).
   - "Rings Dips" sub-section: "Support Hold" and "Maltese Hold" got
     equipment="Rings" from the sub-section header, same reasoning.
   - "Planche" and "Planche Pushups" sub-sections are titled "...--
     Parallel Bars and Floor" in the book -- a dual-equipment label with
     no clean single value. Defaulted non-Rings entries in both to
     "Parallel Bars" (planche work is primarily trained on parallettes
     in this book) rather than "Floor". progression_line for these two
     was recorded as "Planche" / "Planche Pushups" -- the "-- Parallel
     Bars and Floor" suffix was treated as an equipment note, not part
     of the chain name.
   - "Rings Kipping Skills" and "Rings Felge Skills" sub-sections: none
     of the individual exercise names say "Rings", but both sections got
     equipment="Rings" from the section header.
   - Several Chapter 27 Muscle-ups entries (the felge and combo-skill
     names: "Felge Backward, Straight-Body to Support/Handstand",
     "Straight-Body Rotation to Handstand", "Straddle Front Lever to
     Muscle-up to Advanced Tuck Planche", "Front Lever Muscle-up to
     Straddle Planche") got the chapter's generic "Bar" default, even
     though felge skills are frequently ring-based in practice -- the
     book's index text doesn't say which equipment for these specific
     entries.
   - Ab Wheel sub-section: the six literal ab-wheel-tool movements
     (Knees/Ramp/Eccentrics/Full/+20lbs./One-Arm Ab Wheel) got
     equipment=NULL, since "Ab Wheel" isn't one of the values documented
     on the model ("Bar"/"Rings"/"Parallel Bars"/"Floor"/"None"). The
     Plank entries in the same sub-section got "Floor" instead, since
     those are bodyweight planks, not the ab-wheel tool itself.
   - Level ranges in the book ("Levels 1-4", "Levels 6-9", "Levels 8 &
     9", "Levels 5+") were collapsed to their first number per your
     instruction; each such row has an inline comment with the original
     range text.

6. `progresses_from_id` is NULL for every row, on purpose (per your
   instruction) -- the index gives level numbers but not an explicit
   chain between progression_line boundaries. TODO: fill these in
   manually once you've confirmed the chains.

7. Section headers with no named/leveled exercise, or explicitly flagged
   in the book's own index as pure cross-references, were skipped
   entirely (no rows generated): "Press / Overhead Press / Military
   Press" (ch.24, intro only), "Weighted Pull-ups" (ch.25, intro only),
   "Weighted Dips" (ch.26, intro only), "Specific Rings Elements" (ch.27,
   explicitly a duplicate cross-reference section per the source text),
   "Flags" (ch.27, no leveled list captured), "Other Leg Exercises" and
   "Miscellaneous Exercises" (ch.27, no leveled list captured).
"""

import sys
from pathlib import Path

# Allow running as `python backend/scripts/seed_exercises.py` from the
# repo root without installing the app package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import psycopg2

from app.config import settings

# Columns: name, movement_pattern, progression_line, level, equipment,
# book_page, level_variant. `id` and `progresses_from_id` are
# deliberately absent -- `id` is left to the column's server_default
# (gen_random_uuid()), and progresses_from_id is NULL for every row (see
# item 6 above). level_variant is None except for the two genuine
# (progression_line, level) collisions noted in item 2 above.
EXERCISES = [
    # --- Chapter 24: Handstand Variations ---
    # Handstands Progression (Static, Floor unless noted)
    ("Wall Handstand", "Static", "Handstands Progression", 1, "Wall", 320, None),  # originally "Levels 1-4"
    ("Headstand", "Static", "Handstands Progression", None, "Floor", 325, None),
    ("Freestanding Handstand", "Static", "Handstands Progression", 5, "Floor", 326, None),
    ("Freestanding Handstand with One-Arm Support", "Static", "Handstands Progression", 6, "Floor", 328, None),  # originally "Levels 6-9"
    ("Freestanding Handstand Shoulder Taps", "Static", "Handstands Progression", None, "Floor", 329, None),
    ("Handstand Walking", "Static", "Handstands Progression", None, "Floor", 330, None),
    ("Hands-Close-Together Handstand", "Static", "Handstands Progression", None, "Floor", 330, None),
    ("One-Arm Handstand", "Static", "Handstands Progression", 10, "Floor", 331, None),

    # Rings Handstands (Static, Rings)
    ("Rings Shoulder Stand", "Static", "Rings Handstands", 5, "Rings", 336, None),
    ("Rings Strap Handstand", "Static", "Rings Handstands", 6, "Rings", 338, None),
    ("Rings Handstand", "Static", "Rings Handstands", 7, "Rings", 339, None),

    # Handstand Pushups (Push, Wall for wall entries else Floor)
    ("Pike Headstand Pushup", "Push", "Handstand Pushups", 1, "Floor", 341, None),
    ("Box Headstand Pushup", "Push", "Handstand Pushups", 2, "Floor", 342, None),
    ("Wall Headstand Pushup Eccentric", "Push", "Handstand Pushups", 3, "Wall", 343, None),
    ("Wall Headstand Pushup", "Push", "Handstand Pushups", 4, "Wall", 344, None),
    ("Wall Handstand Pushup", "Push", "Handstand Pushups", 5, "Wall", 345, None),
    ("Freestanding Headstand Pushup", "Push", "Handstand Pushups", 6, "Floor", 347, None),
    ("Freestanding Handstand Pushup", "Push", "Handstand Pushups", 7, "Floor", 348, None),

    # Rings Handstand Pushups (Push, Rings)
    ("Rings Wide Handstand Pushup", "Push", "Rings Handstand Pushups", 7, "Rings", 349, None),
    ("Rings Strap Handstand Pushup (with Elbows In)", "Push", "Rings Handstand Pushups", 8, "Rings", 350, None),
    ("Rings Freestanding Handstand Pushup", "Push", "Rings Handstand Pushups", 9, "Rings", 351, None),

    # "Press / Overhead Press / Military Press" skipped: intro only, no exercise (p.352)

    # Bent-Arm Press to Handstands (Push, Floor unless PB)
    ("Bent-Arm, Bent-Body Press to Handstand", "Push", "Bent-Arm Press to Handstands", 5, "Floor", 353, None),
    ("L-Sit Bent-Arm, Bent-Body Press to Handstand", "Push", "Bent-Arm Press to Handstands", 6, "Floor", 355, None),
    ("Chest Roll, Straight-Body Press to Handstand", "Push", "Bent-Arm Press to Handstands", 7, "Floor", 356, None),
    ("Bent-Arm, Straight-Body Press to Handstand", "Push", "Bent-Arm Press to Handstands", 8, "Floor", 357, None),
    ("Handstand to Elbow Lever to Handstand", "Push", "Bent-Arm Press to Handstands", 9, "Floor", 358, None),
    ("Parallel Bar Dip, Straight-Body Press to Handstand", "Push", "Bent-Arm Press to Handstands", 10, "Parallel Bars", 359, None),

    # Rings Bent-Arm Press to Handstands (Push, Rings)
    ("Chair Handstand", "Push", "Rings Bent-Arm Press to Handstands", 6, "Rings", 360, None),  # JUDGMENT: Rings via section header, not literal name
    ("Illusion Chair Handstand", "Push", "Rings Bent-Arm Press to Handstands", 7, "Rings", 362, None),  # JUDGMENT: Rings via section header
    ("Rings Bent-Arm, Bent-Body Press to Handstand", "Push", "Rings Bent-Arm Press to Handstands", 8, "Rings", 364, None),
    ("Rings Dip to Handstand", "Push", "Rings Bent-Arm Press to Handstands", 9, "Rings", 365, None),
    ("Rings Bent-Arm, Straight-Body Press to Handstand", "Push", "Rings Bent-Arm Press to Handstands", 10, "Rings", 366, None),
    ("Rings Handstand to Elbow Lever to Handstand", "Push", "Rings Bent-Arm Press to Handstands", 11, "Rings", 367, None),
    ("Rings Dip, Straight-Body Press to Handstand", "Push", "Rings Bent-Arm Press to Handstands", 12, "Rings", 368, None),

    # Straight-Arm Press to Handstands (Push, Floor unless Rings/Wall)
    ("Wall Straddle Press to Handstand Eccentrics", "Push", "Straight-Arm Press to Handstands", 5, "Wall", 369, None),
    ("Elevated Straddle Stand, Straddle Press to Handstand", "Push", "Straight-Arm Press to Handstands", 6, "Floor", 371, None),
    ("Straddle or Pike Stand, Press to Handstand", "Push", "Straight-Arm Press to Handstands", 7, "Floor", 373, None),
    ("L-Sit / Straddle-L, Straddle Press to Handstand", "Push", "Straight-Arm Press to Handstands", 8, "Floor", 374, None),
    ("L-Sit / Straddle-L Pike Press to Handstand", "Push", "Straight-Arm Press to Handstands", 9, "Floor", 375, None),
    ("Rings Straight-Arm, L-Sit, Straddle Press to Handstand", "Push", "Straight-Arm Press to Handstands", 10, "Rings", 376, None),
    ("Rings Straight-Arm, Straddle-L, Straddle Press to Handstand", "Push", "Straight-Arm Press to Handstands", 11, "Rings", 377, None),
    ("Rings Straight-Arm, Pike Press to Handstand", "Push", "Straight-Arm Press to Handstands", 12, "Rings", 378, None),

    # --- Chapter 25: Pulling Exercises ---
    # movement_pattern="Pull" applied to every sub-section below, per the
    # chapter-level rule, EXCEPT L-Sit/Straddle-L/V-Sits/Manna, Back
    # Lever, Front Lever, and Front Lever Rows, which are "Static" -- see
    # item 3 above.

    # L-Sit / Straddle-L / V-Sits / Manna (Static; equipment overridden to Floor -- see docstring)
    ("Tuck L-Sit", "Static", "L-Sit / Straddle-L / V-Sits / Manna", 1, "Floor", 380, None),  # JUDGMENT: Floor override, not chapter default Bar
    ("One-Leg-Bent L-Sit", "Static", "L-Sit / Straddle-L / V-Sits / Manna", 2, "Floor", 381, None),  # JUDGMENT: Floor override
    ("L-Sit", "Static", "L-Sit / Straddle-L / V-Sits / Manna", 3, "Floor", 382, None),  # JUDGMENT: Floor override
    ("Straddle L-Sit", "Static", "L-Sit / Straddle-L / V-Sits / Manna", 4, "Floor", 383, None),  # JUDGMENT: Floor override
    ("Rings-Turned-Out L-Sit", "Static", "L-Sit / Straddle-L / V-Sits / Manna", 5, "Rings", 384, None),

    # Back Lever (Static; equipment defaulted to Bar -- see docstring)
    ("German Hang", "Static", "Back Lever", 1, "Bar", 391, None),  # JUDGMENT: Bar default, could be Rings
    ("Skin the Cat", "Static", "Back Lever", 2, "Bar", 392, None),  # JUDGMENT: Bar default
    ("Tuck Back Lever", "Static", "Back Lever", 3, "Bar", 393, None),  # JUDGMENT: Bar default
    ("Advanced Tuck Back Lever", "Static", "Back Lever", 4, "Bar", 394, None),  # JUDGMENT: Bar default
    ("Straddle Back Lever", "Static", "Back Lever", 5, "Bar", 395, None),  # JUDGMENT: Bar default
    ("Half Layout / One-Leg-Out Back Lever", "Static", "Back Lever", 6, "Bar", 396, None),  # JUDGMENT: Bar default
    ("Full Back Lever", "Static", "Back Lever", 7, "Bar", 397, None),  # JUDGMENT: Bar default
    ("Back Lever Pullout", "Static", "Back Lever", 8, "Bar", 398, None),  # JUDGMENT: Bar default
    ("German Hang Pullout", "Static", "Back Lever", 9, "Bar", 399, None),  # JUDGMENT: Bar default
    ("Bent-Arm Pull-up to Back Lever", "Static", "Back Lever", 10, "Bar", 400, None),  # JUDGMENT: Bar default
    ("Handstand Lower to Back Lever", "Static", "Back Lever", 11, "Bar", 401, None),  # JUDGMENT: Bar default

    # Front Lever (Static; equipment defaulted to Bar -- see docstring)
    ("Tuck Front Lever", "Static", "Front Lever", 4, "Bar", 402, None),  # JUDGMENT: Bar default
    ("Advanced Tuck Front Lever", "Static", "Front Lever", 5, "Bar", 403, None),  # JUDGMENT: Bar default
    ("Straddle Front Lever", "Static", "Front Lever", 6, "Bar", 404, None),  # JUDGMENT: Bar default
    ("Half Layout / One-Leg-Out Front Lever", "Static", "Front Lever", 7, "Bar", 405, None),  # JUDGMENT: Bar default
    ("Full Front Lever", "Static", "Front Lever", 8, "Bar", 406, None),  # JUDGMENT: Bar default
    ("Front Lever Pull to Inverted Hang", "Static", "Front Lever", 9, "Bar", 407, None),  # JUDGMENT: Bar default
    ("Hang Pull to Inverted Hang", "Static", "Front Lever", 10, "Bar", 408, None),  # JUDGMENT: Bar default
    ("Circle Front Levers", "Static", "Front Lever", 11, "Bar", 409, None),  # JUDGMENT: Bar default

    # Front Lever Rows (Static; equipment defaulted to Bar -- see docstring)
    ("Tuck Front Lever Rows", "Static", "Front Lever Rows", 5, "Bar", 410, None),  # JUDGMENT: Bar default
    ("Advanced Tuck Front Lever Rows", "Static", "Front Lever Rows", 6, "Bar", 411, None),  # JUDGMENT: Bar default
    ("Straddle Front Lever Rows", "Static", "Front Lever Rows", 8, "Bar", 412, None),  # JUDGMENT: Bar default
    ("Hang to Front Lever Row", "Static", "Front Lever Rows", 9, "Bar", 413, None),  # JUDGMENT: Bar default
    ("Full Front Lever Rows", "Static", "Front Lever Rows", 10, "Bar", 414, None),  # JUDGMENT: Bar default
    ("Rope Climb Front Lever Rows", "Static", "Front Lever Rows", None, "Bar", 414, None),  # JUDGMENT: actually rope-based, no "Rope" equipment value exists yet

    # Rowing (Pull; Rings; last two via section context)
    ("Ring Row Eccentrics", "Pull", "Rowing", 1, "Rings", 416, None),
    ("Ring Rows", "Pull", "Rowing", 2, "Rings", 417, None),
    ("Wide Ring Rows", "Pull", "Rowing", 3, "Rings", 418, None),
    ("Archer Ring Rows", "Pull", "Rowing", 4, "Rings", 419, None),
    ("Archer-Arm-In Ring Rows", "Pull", "Rowing", 5, "Rings", 420, None),
    ("Straddle One-Arm Rows", "Pull", "Rowing", 6, "Rings", 421, None),  # JUDGMENT: Rings via section context, not literal name
    ("One-Arm Rows", "Pull", "Rowing", 7, "Rings", 422, None),  # JUDGMENT: Rings via section context

    # Pull-ups (Pull; Bar)
    ("Jumping Pull-ups", "Pull", "Pull-ups", 1, "Bar", 423, None),
    ("Bar Pull-up Eccentrics", "Pull", "Pull-ups", 2, "Bar", 424, None),
    ("Bar Pull-ups", "Pull", "Pull-ups", 3, "Bar", 425, None),
    ("L-Sit Pull-ups", "Pull", "Pull-ups", 4, "Bar", 426, None),
    ("Pullover", "Pull", "Pull-ups", 5, "Bar", 427, None),

    # Ring Pull-ups + One-Arm Chin-ups (Pull; mixed Rings / Bar)
    ("Rings L-Sit Pull-ups", "Pull", "Ring Pull-ups + One-Arm Chin-ups", 4, "Rings", 428, None),
    ("Rings Wide Grip Pull-ups", "Pull", "Ring Pull-ups + One-Arm Chin-ups", 5, "Rings", 429, None),
    ("Rings Wide Grip L-Sit Pull-ups", "Pull", "Ring Pull-ups + One-Arm Chin-ups", 6, "Rings", 429, None),
    ("Rings Archer Pull-ups", "Pull", "Ring Pull-ups + One-Arm Chin-ups", 7, "Rings", 430, None),
    ("One-Arm Chin-up / Pull-up Eccentrics", "Pull", "Ring Pull-ups + One-Arm Chin-ups", 8, "Bar", 431, None),  # JUDGMENT: Bar, disambiguated from Rings half of this progression_line
    ("One-Arm Chin-up", "Pull", "Ring Pull-ups + One-Arm Chin-ups", 9, "Bar", 434, None),  # JUDGMENT: Bar
    ("One-Arm Chin-up +15 lbs.", "Pull", "Ring Pull-ups + One-Arm Chin-ups", 10, "Bar", 434, None),  # JUDGMENT: Bar
    ("One-Arm Chin-up +25 lbs.", "Pull", "Ring Pull-ups + One-Arm Chin-ups", 11, "Bar", 434, None),  # JUDGMENT: Bar

    # "Weighted Pull-ups" skipped: intro only, no single leveled exercise (p.436)

    # Explosive Pull-ups (Pull; Bar)
    ("Kipping Pull-ups", "Pull", "Explosive Pull-ups", 2, "Bar", 437, None),
    ("Bar Pull-ups (Explosive)", "Pull", "Explosive Pull-ups", 3, "Bar", 438, None),  # renamed to disambiguate from the Pull-ups line's "Bar Pull-ups" (same name, same level, book p.425 vs p.438)
    ("Kipping Clapping Pull-ups", "Pull", "Explosive Pull-ups", 4, "Bar", 439, None),
    ("Non-Kipping Clapping Pull-ups", "Pull", "Explosive Pull-ups", 5, "Bar", 440, None),
    ("L-Sit Clapping Pull-ups", "Pull", "Explosive Pull-ups", 6, "Bar", 441, None),
    ("Kipping, Behind-the-Back Clapping Pull-ups", "Pull", "Explosive Pull-ups", 7, "Bar", 442, None),
    ("L-Sit, Slap-the-Abdominals Pull-ups", "Pull", "Explosive Pull-ups", 8, "Bar", 443, None),
    ("L-Sit, Slap-the-Thighs Pull-ups", "Pull", "Explosive Pull-ups", 9, "Bar", 444, None),
    ("Straight-Body, Slap-the-Thighs Pull-ups", "Pull", "Explosive Pull-ups", 10, "Bar", 445, None),
    ("Non-Kipping, Behind-the-Back Clapping Pull-ups", "Pull", "Explosive Pull-ups", 11, "Bar", 446, None),

    # Iron Cross (Pull; Rings via section context -- Iron Cross is rings-only by definition)
    ("Iron Cross Progressions", "Pull", "Iron Cross", 9, "Rings", 448, None),  # JUDGMENT: Rings via section context
    ("Hold Iron Cross", "Pull", "Iron Cross", 10, "Rings", 451, None),  # JUDGMENT: Rings via section context
    ("Iron Cross to Back Lever", "Pull", "Iron Cross", 11, "Rings", 452, None),  # JUDGMENT: Rings via section context
    ("Iron Cross Pullouts", "Pull", "Iron Cross", 13, "Rings", 453, None),  # JUDGMENT: Rings via section context
    ("Hang Pull to Back Lever", "Pull", "Iron Cross", 14, "Rings", 454, None),  # JUDGMENT: Rings via section context
    ("Butterfly Mount", "Pull", "Iron Cross", 15, "Rings", 455, None),  # JUDGMENT: Rings via section context
    ("Support Hold to Hang to Iron Cross", "Pull", "Iron Cross", 16, "Rings", 456, None),  # JUDGMENT: Rings via section context

    # --- Chapter 26: Pushing Variations ---
    # Planche -- progression_line "Planche" (the "-- Parallel Bars and
    # Floor" book heading is treated as an equipment note, not part of
    # the chain name); non-Rings entries defaulted to Parallel Bars.
    ("Frog Stand", "Push", "Planche", 3, "Parallel Bars", 458, None),  # JUDGMENT: Parallel Bars default (section covers PB and Floor)
    ("Straight-Arm Frog Stand", "Push", "Planche", 4, "Parallel Bars", 459, None),  # JUDGMENT: Parallel Bars default
    ("Tuck Planche", "Push", "Planche", 5, "Parallel Bars", 460, None),  # JUDGMENT: Parallel Bars default
    ("Advanced Tuck Planche", "Push", "Planche", 6, "Parallel Bars", 461, None),  # JUDGMENT: Parallel Bars default
    ("Pseudo Planche Pushups", "Push", "Planche", None, "Parallel Bars", 462, None),  # JUDGMENT: Parallel Bars default
    ("Band-Assisted Planche", "Push", "Planche", None, "Parallel Bars", 463, None),  # JUDGMENT: Parallel Bars default
    ("Straddle Planche", "Push", "Planche", 8, "Parallel Bars", 464, None),  # JUDGMENT: Parallel Bars default
    ("Half Layout / One-Leg-Out Planche", "Push", "Planche", 9, "Parallel Bars", 465, None),  # JUDGMENT: Parallel Bars default
    ("Full Planche", "Push", "Planche", 11, "Parallel Bars", 466, None),  # JUDGMENT: Parallel Bars default
    ("Straight-Arm Straddle Planche to Handstand", "Push", "Planche", 12, "Parallel Bars", 467, None),  # JUDGMENT: Parallel Bars default
    ("Rings Straight-Arm Straddle Planche to Handstand", "Push", "Planche", 14, "Rings", 468, None),
    ("Straight-Arm, Straight-Body from Planche to Handstand", "Push", "Planche", 15, "Parallel Bars", 469, None),  # JUDGMENT: Parallel Bars default
    ("Rings Straight-Arm, Straight-Body Press to Handstand", "Push", "Planche", 16, "Rings", 470, "a"),  # book assigns Level 16 to two exercises in this line; see item 2
    ("Rings Straight-Arm, Straight-Body from Planche to Handstand", "Push", "Planche", 16, "Rings", 471, "b"),  # book assigns Level 16 to two exercises in this line; see item 2

    # Rings Planche (Rings)
    ("Rings Frog Stand", "Push", "Rings Planche", 4, "Rings", 472, None),
    ("Rings Straight-Arm Frog Stand", "Push", "Rings Planche", 5, "Rings", 473, None),
    ("Rings Tuck Planche", "Push", "Rings Planche", 6, "Rings", 474, None),
    ("Rings Advanced Tuck Planche", "Push", "Rings Planche", 8, "Rings", 475, None),
    ("Rings Straddle Planche", "Push", "Rings Planche", 10, "Rings", 476, None),
    ("Rings Half Layout / One-Leg-Out Planche", "Push", "Rings Planche", 12, "Rings", 477, None),
    ("Rings Full Planche", "Push", "Rings Planche", 14, "Rings", 477, None),

    # Planche Pushups -- progression_line "Planche Pushups" (same equipment-note handling as Planche above)
    ("Tuck Planche Pushups", "Push", "Planche Pushups", 6, "Parallel Bars", 479, None),  # JUDGMENT: Parallel Bars default
    ("Advanced Tuck Planche Pushups", "Push", "Planche Pushups", 8, "Parallel Bars", 480, None),  # JUDGMENT: Parallel Bars default
    ("Straddle Planche Pushups", "Push", "Planche Pushups", 10, "Parallel Bars", 480, None),  # JUDGMENT: Parallel Bars default
    ("Half Layout / One-Leg-Out Planche Pushups", "Push", "Planche Pushups", 12, "Parallel Bars", 481, None),  # JUDGMENT: Parallel Bars default
    ("Full Planche Pushups", "Push", "Planche Pushups", 14, "Parallel Bars", 482, None),  # JUDGMENT: Parallel Bars default

    # Rings Planche Pushups (Rings)
    ("Rings Tuck Planche Pushups", "Push", "Rings Planche Pushups", 8, "Rings", 483, None),
    ("Rings Advanced Tuck Planche Pushups", "Push", "Rings Planche Pushups", 10, "Rings", 483, None),
    ("Rings Straddle Planche Pushups", "Push", "Rings Planche Pushups", 12, "Rings", 483, None),
    ("Rings Half Layout / One-Leg-Out Planche Pushups", "Push", "Rings Planche Pushups", 14, "Rings", 484, None),
    ("Rings Full Planche Pushups", "Push", "Rings Planche Pushups", 16, "Rings", 484, None),

    # Pushups (Floor default, Rings/Wall explicit; Rings takes precedence over Wall)
    ("Standard Pushups", "Push", "Pushups", 1, "Floor", 485, None),
    ("Diamond Pushups", "Push", "Pushups", 2, "Floor", 486, None),
    ("Rings Wide Pushups", "Push", "Pushups", 3, "Rings", 486, None),
    ("Rings Pushups", "Push", "Pushups", 4, "Rings", 487, None),
    ("Rings-Turned-Out Pushups", "Push", "Pushups", 5, "Rings", 488, None),
    ("Rings-Turned-Out Archer Pushups", "Push", "Pushups", 6, "Rings", 489, None),
    ("Rings-Turned-Out, 40-Degree-Lean Pseudo Planche Pushups", "Push", "Pushups", 7, "Rings", 490, None),
    ("Rings-Turned-Out, 60-Degree-Lean Pseudo Planche Pushups", "Push", "Pushups", 8, "Rings", 491, None),
    ("Rings-Turned-Out Maltese Pushups", "Push", "Pushups", 9, "Rings", 492, None),
    ("Wall Pseudo Planche Pushups", "Push", "Pushups", 10, "Wall", 493, None),
    ("Rings Wall Pseudo Planche Pushups", "Push", "Pushups", 11, "Rings", 494, None),  # Rings takes precedence over Wall
    ("Wall Maltese Pushups", "Push", "Pushups", 12, "Wall", 495, None),
    ("Rings Wall Maltese Pushups", "Push", "Pushups", 13, "Rings", 496, None),  # Rings takes precedence over Wall
    ("Clapping Pushup Variations", "Push", "Pushups", None, "Floor", 497, None),

    # One-Arm Pushups (Floor default, Rings explicit)
    ("Hands-Elevated, One-Arm Pushup", "Push", "One-Arm Pushups", 5, "Floor", 499, None),
    ("Straddle One-Arm Pushup", "Push", "One-Arm Pushups", 6, "Floor", 501, None),
    ("Rings Straddle One-Arm Pushup", "Push", "One-Arm Pushups", 7, "Rings", 502, None),
    ("Straight-Body, One-Arm Pushup", "Push", "One-Arm Pushups", 8, "Floor", 503, None),
    ("Rings Straight-Body, One-Arm Pushup", "Push", "One-Arm Pushups", 9, "Rings", 504, None),

    # Dips (Parallel Bars; 3 entries via section context)
    ("Parallel Bar Jumping Dips", "Push", "Dips", 1, "Parallel Bars", 505, None),
    ("Parallel Bar Dip Eccentrics", "Push", "Dips", 2, "Parallel Bars", 506, None),
    ("Parallel Bar Dips", "Push", "Dips", 3, "Parallel Bars", 507, None),
    ("L-Sit Dips", "Push", "Dips", 4, "Parallel Bars", 508, None),  # JUDGMENT: Parallel Bars via section context, not literal name
    ("45-Degree Forward-Lean Dips", "Push", "Dips", 5, "Parallel Bars", 509, None),  # JUDGMENT: Parallel Bars via section context
    ("One-Arm Dip", "Push", "Dips", 8, "Parallel Bars", 510, None),  # originally "Levels 8 & 9"; JUDGMENT: Parallel Bars via section context

    # Rings Dips (Rings; 2 entries via section context)
    ("Support Hold", "Push", "Rings Dips", 1, "Rings", 512, None),  # JUDGMENT: Rings via section context, not literal name
    ("Rings-Turned-Out Support Hold", "Push", "Rings Dips", 2, "Rings", 513, None),
    ("Rings Dip Eccentrics", "Push", "Rings Dips", 3, "Rings", 514, None),
    ("Rings Dips", "Push", "Rings Dips", 4, "Rings", 515, None),
    ("Rings L-Sit Dips", "Push", "Rings Dips", 5, "Rings", 516, None),
    ("Rings Wide Dips", "Push", "Rings Dips", 6, "Rings", 517, None),
    ("Rings-Turned-Out Dip Variations", "Push", "Rings Dips", None, "Rings", 518, None),
    ("Maltese Hold", "Push", "Rings Dips", 17, "Rings", 520, None),  # JUDGMENT: Rings via section context

    # "Weighted Dips" skipped: intro only, no single leveled exercise (p.521)

    # --- Chapter 27: Multi-Plane Exercises, Core, and Legs ---
    # Muscle-ups and Inverted Muscle-ups (Pull per explicit chapter instruction; Bar default)
    ("Muscle-up Negatives", "Pull", "Muscle-ups and Inverted Muscle-ups", 3, "Bar", 525, None),
    ("Kipping Muscle-ups", "Pull", "Muscle-ups and Inverted Muscle-ups", 4, "Bar", 526, None),
    ("Muscle-ups", "Pull", "Muscle-ups and Inverted Muscle-ups", 5, "Bar", 527, None),
    ("Wide / No-False-Grip Muscle-ups", "Pull", "Muscle-ups and Inverted Muscle-ups", 6, "Bar", 528, None),
    ("Strict Bar Muscle-Ups", "Pull", "Muscle-ups and Inverted Muscle-ups", 7, "Bar", 529, None),
    ("Straddle Front Lever to Muscle-up to Advanced Tuck Planche", "Pull", "Muscle-ups and Inverted Muscle-ups", 8, "Bar", 530, "a"),  # book assigns Level 8 to two exercises in this line; see item 2; JUDGMENT: Bar default, complex combo skill
    ("L-Sit Muscle-up", "Pull", "Muscle-ups and Inverted Muscle-ups", 8, "Bar", 531, "b"),  # book assigns Level 8 to two exercises in this line; see item 2
    ("One-Arm-Straight Muscle-up", "Pull", "Muscle-ups and Inverted Muscle-ups", 9, "Bar", 532, None),
    ("Felge Backward, Straight-Body to Support", "Pull", "Muscle-ups and Inverted Muscle-ups", 10, "Bar", 533, None),  # JUDGMENT: Bar default, felge is often rings-based
    ("Front Lever Muscle-up to Straddle Planche", "Pull", "Muscle-ups and Inverted Muscle-ups", 11, "Bar", 534, None),
    ("Felge Backward, Straight-Body to Handstand", "Pull", "Muscle-ups and Inverted Muscle-ups", 12, "Bar", 535, None),  # JUDGMENT: Bar default, felge is often rings-based
    ("Straight-Body Rotation to Handstand", "Pull", "Muscle-ups and Inverted Muscle-ups", 14, "Bar", 536, None),  # JUDGMENT: Bar default, ambiguous
    ("Butterfly Mount (Muscle-ups)", "Pull", "Muscle-ups and Inverted Muscle-ups", 15, "Bar", 536, None),  # renamed to disambiguate from the Iron Cross line's "Butterfly Mount" (same name, same level, book p.455 vs p.536)
    ("Elevator / Inverted Muscle-up to Handstand", "Pull", "Muscle-ups and Inverted Muscle-ups", 17, "Bar", 538, None),

    # Elbow Levers (Static; Floor default, Rings explicit)
    ("Two-Arm Elbow Lever", "Static", "Elbow Levers", 5, "Floor", 539, None),
    ("Rings Two-Arm Elbow Lever", "Static", "Elbow Levers", 6, "Rings", 540, None),
    ("One-Arm Straddle Elbow Lever", "Static", "Elbow Levers", 7, "Floor", 541, None),
    ("One-Arm, Straight-Body Elbow Lever", "Static", "Elbow Levers", 8, "Floor", 542, None),

    # "Flags" skipped: no leveled list captured in index (p.543)

    # Ab Wheel (Core; Floor for planks, equipment=NULL for the ab-wheel-tool items)
    ("25s Plank", "Core", "Ab Wheel", 2, "Floor", 545, None),
    ("60s Plank", "Core", "Ab Wheel", 3, "Floor", 545, None),
    ("One-Arm, One-Leg Plank", "Core", "Ab Wheel", 4, "Floor", 545, None),
    ("Knees Ab Wheel", "Core", "Ab Wheel", 5, None, 546, None),  # JUDGMENT: "Ab Wheel" equipment not in the documented value set (Bar/Rings/Parallel Bars/Floor/None)
    ("Ramp Ab Wheel", "Core", "Ab Wheel", 6, None, 546, None),  # JUDGMENT: same as above
    ("Ab Wheel Eccentrics", "Core", "Ab Wheel", 7, None, 546, None),  # JUDGMENT: same as above
    ("Full Ab Wheel", "Core", "Ab Wheel", 8, None, 546, None),  # JUDGMENT: same as above
    ("Ab Wheel + 20 lbs.", "Core", "Ab Wheel", 9, None, 546, None),  # JUDGMENT: same as above
    ("One-Arm Ab Wheel", "Core", "Ab Wheel", 10, None, 546, None),  # JUDGMENT: same as above

    # "Specific Rings Elements" skipped entirely: explicitly a duplicate
    # cross-reference section per the source text (p.549-550), re-listing
    # exercises already defined under their own progression lines above.

    # Rings Kipping Skills (Pull; Rings via section context)
    ("Kip to Support", "Pull", "Rings Kipping Skills", 6, "Rings", 551, None),  # JUDGMENT: Rings via section context
    ("Back Kip to Support", "Pull", "Rings Kipping Skills", 7, "Rings", 553, None),  # JUDGMENT: Rings via section context
    ("Straight-Arm Kip to L-Sit", "Pull", "Rings Kipping Skills", 9, "Rings", 554, None),  # JUDGMENT: Rings via section context
    ("Straight-Arm Back Kip to Support", "Pull", "Rings Kipping Skills", 10, "Rings", 555, None),  # JUDGMENT: Rings via section context
    ("Back Kip to Handstand", "Pull", "Rings Kipping Skills", 11, "Rings", 556, None),  # JUDGMENT: Rings via section context
    ("Straight-Arm Kip to V-Sit / Kip to Cross or L-Sit Cross", "Pull", "Rings Kipping Skills", 13, "Rings", 557, None),  # JUDGMENT: Rings via section context
    ("Back Kip to Cross or L-Sit Cross", "Pull", "Rings Kipping Skills", 14, "Rings", 558, None),  # JUDGMENT: Rings via section context
    ("Back Kip to Straddle Planche", "Pull", "Rings Kipping Skills", 15, "Rings", 559, None),  # JUDGMENT: Rings via section context

    # Rings Felge Skills (Pull; Rings via section context)
    ("Felge Forward to Support (Piked Body)", "Pull", "Rings Felge Skills", 6, "Rings", 561, None),  # JUDGMENT: Rings via section context
    ("Felge Backward to Support (Piked Body)", "Pull", "Rings Felge Skills", 7, "Rings", 562, None),  # JUDGMENT: Rings via section context
    ("Felge Forward to Support (Straight Body)", "Pull", "Rings Felge Skills", 9, "Rings", 563, None),  # JUDGMENT: Rings via section context
    ("Felge Backward to Support (Straight Body)", "Pull", "Rings Felge Skills", 10, "Rings", 564, None),  # JUDGMENT: Rings via section context
    ("Felge Backward to Handstand (Straight Body)", "Pull", "Rings Felge Skills", 12, "Rings", 565, None),  # JUDGMENT: Rings via section context
    ("Felge Forward to Cross (Straight-Arm, Bent Body)", "Pull", "Rings Felge Skills", 13, "Rings", 566, None),  # JUDGMENT: Rings via section context
    ("Felge Forward to Straddle Planche (Straight-Arm)", "Pull", "Rings Felge Skills", 14, "Rings", 567, None),  # JUDGMENT: Rings via section context
    ("Felge Forward to Handstand (Straight-Arm, Straight-Body)", "Pull", "Rings Felge Skills", 15, "Rings", 568, None),  # JUDGMENT: Rings via section context

    # Squats (Legs; Floor)
    ("Asian Squat", "Legs", "Squats", None, "Floor", 569, None),
    ("Parallel Squat", "Legs", "Squats", 1, "Floor", 570, None),
    ("Full Squat", "Legs", "Squats", 2, "Floor", 571, None),
    ("Side-to-Side Squat", "Legs", "Squats", 3, "Floor", 572, None),
    ("Pistols (Single-Leg Squats)", "Legs", "Squats", 4, "Floor", 573, None),
    ("Weighted Pistols", "Legs", "Squats", 5, "Floor", 575, None),  # originally "Levels 5+"

    # "Other Leg Exercises" (p.576) and "Miscellaneous Exercises" (p.579)
    # skipped: no leveled list captured in index.
]

INSERT_SQL = """
    INSERT INTO exercise
        (name, movement_pattern, progression_line, level, equipment, book_page, level_variant)
    VALUES
        (%s, %s, %s, %s, %s, %s, %s)
"""


def main() -> None:
    conn = psycopg2.connect(
        host=settings.cockroach_host,
        port=settings.cockroach_port,
        user=settings.cockroach_user,
        password=settings.cockroach_password,
        dbname=settings.cockroach_database,
        sslmode="disable",
    )
    try:
        with conn:
            with conn.cursor() as cur:
                cur.executemany(INSERT_SQL, EXERCISES)
        print(f"Inserted {len(EXERCISES)} rows into exercise.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
