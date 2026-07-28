I extracted the exercise index from Steven Low's "Overcoming Gravity" 2nd
Edition (chapters 24-27), which lists every named exercise with its
progression level, grouped by movement pattern and progression line. Below
is the raw index text (names, levels, page numbers, and section headers
only -- no technique descriptions, just the structural index) so you can
turn it into seed data for the `exercise` table.

For each exercise, derive:
- name: the exercise name as listed (e.g. "Rings Archer Pull-ups")
- movement_pattern: from the chapter it's under (Chapter 24 -> "Static"
  for handstand holds, or "Push" if it's a pressing movement to
  handstand -- use judgment per exercise; Chapter 25 -> "Pull"; Chapter 26
  -> "Push"; Chapter 27 -> split between "Core", "Legs", or "Static"
  depending on the sub-section, e.g. Squats -> "Legs", L-Sit/Front
  Lever/Back Lever/Elbow Levers/Flags -> "Static", Muscle-ups -> "Pull")
- progression_line: the sub-section header it's under (e.g. "Pull-ups" vs.
  "Ring Pull-ups + One-Arm Chin-ups" are two separate progression_lines
  per the book's own grouping -- preserve the book's own sub-section names,
  don't invent new groupings)
- level: the numeric level given (some say "N/A" -- set level to NULL for
  those, don't force a number; some give a range like "Levels 8 & 9" or
  "Levels 5+" -- use the first number and add a one-line comment noting
  the original range)
- equipment: infer from the name -- "Rings" if it says Rings, "Parallel
  Bars" if it says Parallel Bar / PB, "Bar" for bar-based pulling
  exercises with no other equipment mentioned, "Wall" for wall-assisted
  variants, "Floor"/NULL otherwise
- book_page: the page number given in the index
- progresses_from: leave this as a TODO comment for now -- the index
  gives level numbers but not always an explicit chain between
  progression_line boundaries. Don't guess this -- flag it as something
  I'll confirm manually later, and leave progresses_from_id NULL for all
  rows for now.

Output this as a Python script (e.g. backend/scripts/seed_exercises.py)
that inserts this data via raw SQL (not the ORM) using the same
COCKROACH_DATABASE connection config already in app/config.py -- this is
intentional, since we already fixed the server_default specifically so
raw SQL inserts work without the ORM generating the UUID.

Do NOT touch models/, schemas/, routes/, or run the script yet -- just
generate it, so I can review the derived movement_pattern/equipment
values before actually loading anything into the database, since some of
those derivations involve judgment calls I want to check.

=== RAW INDEX TEXT START ===

CHAPTER 24: HANDSTAND VARIATIONS

Handstands Progression
Wall Handstand -- Levels 1-4 (p.320)
Headstand -- Level N/A (p.325)
Freestanding Handstand -- Level 5 (p.326)
Freestanding Handstand with One-Arm Support -- Levels 6-9 (p.328)
Freestanding Handstand Shoulder Taps -- Level N/A (p.329)
Handstand Walking -- Level N/A (p.330)
Hands-Close-Together Handstand -- Level N/A (p.330)
One-Arm Handstand -- Level 10 (p.331)

Rings Handstands
Rings Shoulder Stand -- Level 5 (p.336)
Rings Strap Handstand -- Level 6 (p.338)
Rings Handstand -- Level 7 (p.339)

Handstand Pushups
Pike Headstand Pushup -- Level 1 (p.341)
Box Headstand Pushup -- Level 2 (p.342)
Wall Headstand Pushup Eccentric -- Level 3 (p.343)
Wall Headstand Pushup -- Level 4 (p.344)
Wall Handstand Pushup -- Level 5 (p.345)
Freestanding Headstand Pushup -- Level 6 (p.347)
Freestanding Handstand Pushup -- Level 7 (p.348)

Rings Handstand Pushups
Rings Wide Handstand Pushup -- Level 7 (p.349)
Rings Strap Handstand Pushup (with Elbows In) -- Level 8 (p.350)
Rings Freestanding Handstand Pushup -- Level 9 (p.351)

Press / Overhead Press / Military Press
(section intro, no leveled exercise directly, p.352)

Bent-Arm Press to Handstands
Bent-Arm, Bent-Body Press to Handstand -- Level 5 (p.353)
L-Sit Bent-Arm, Bent-Body Press to Handstand -- Level 6 (p.355)
Chest Roll, Straight-Body Press to Handstand -- Level 7 (p.356)
Bent-Arm, Straight-Body Press to Handstand -- Level 8 (p.357)
Handstand to Elbow Lever to Handstand -- Level 9 (p.358)
Parallel Bar Dip, Straight-Body Press to Handstand -- Level 10 (p.359)

Rings Bent-Arm Press to Handstands
Chair Handstand -- Level 6 (p.360)
Illusion Chair Handstand -- Level 7 (p.362)
Rings Bent-Arm, Bent-Body Press to Handstand -- Level 8 (p.364)
Rings Dip to Handstand -- Level 9 (p.365)
Rings Bent-Arm, Straight-Body Press to Handstand -- Level 10 (p.366)
Rings Handstand to Elbow Lever to Handstand -- Level 11 (p.367)
Rings Dip, Straight-Body Press to Handstand -- Level 12 (p.368)

Straight-Arm Press to Handstands
Wall Straddle Press to Handstand Eccentrics -- Level 5 (p.369)
Elevated Straddle Stand, Straddle Press to Handstand -- Level 6 (p.371)
Straddle or Pike Stand, Press to Handstand -- Level 7 (p.373)
L-Sit / Straddle-L, Straddle Press to Handstand -- Level 8 (p.374)
L-Sit / Straddle-L Pike Press to Handstand -- Level 9 (p.375)
Rings Straight-Arm, L-Sit, Straddle Press to Handstand -- Level 10 (p.376)
Rings Straight-Arm, Straddle-L, Straddle Press to Handstand -- Level 11 (p.377)
Rings Straight-Arm, Pike Press to Handstand -- Level 12 (p.378)

CHAPTER 25: PULLING EXERCISES

L-Sit / Straddle-L / V-Sits / Manna
Tuck L-Sit -- Level 1 (p.380)
One-Leg-Bent L-Sit -- Level 2 (p.381)
L-Sit -- Level 3 (p.382)
Straddle L-Sit -- Level 4 (p.383)
Rings-Turned-Out L-Sit -- Level 5 (p.384)
Training Toward the V-Sit and Manna -- (p.385, no single level)

Back Lever
German Hang -- Level 1 (p.391)
Skin the Cat -- Level 2 (p.392)
Tuck Back Lever -- Level 3 (p.393)
Advanced Tuck Back Lever -- Level 4 (p.394)
Straddle Back Lever -- Level 5 (p.395)
Half Layout / One-Leg-Out Back Lever -- Level 6 (p.396)
Full Back Lever -- Level 7 (p.397)
Back Lever Pullout -- Level 8 (p.398)
German Hang Pullout -- Level 9 (p.399)
Bent-Arm Pull-up to Back Lever -- Level 10 (p.400)
Handstand Lower to Back Lever -- Level 11 (p.401)

Front Lever
Tuck Front Lever -- Level 4 (p.402)
Advanced Tuck Front Lever -- Level 5 (p.403)
Straddle Front Lever -- Level 6 (p.404)
Half Layout / One-Leg-Out Front Lever -- Level 7 (p.405)
Full Front Lever -- Level 8 (p.406)
Front Lever Pull to Inverted Hang -- Level 9 (p.407)
Hang Pull to Inverted Hang -- Level 10 (p.408)
Circle Front Levers -- Level 11 (p.409)

Front Lever Rows
Tuck Front Lever Rows -- Level 5 (p.410)
Advanced Tuck Front Lever Rows -- Level 6 (p.411)
Straddle Front Lever Rows -- Level 8 (p.412)
Hang to Front Lever Row -- Level 9 (p.413)
Full Front Lever Rows -- Level 10 (p.414)
Rope Climb Front Lever Rows -- Level N/A (p.414)

Rowing
Ring Row Eccentrics -- Level 1 (p.416)
Ring Rows -- Level 2 (p.417)
Wide Ring Rows -- Level 3 (p.418)
Archer Ring Rows -- Level 4 (p.419)
Archer-Arm-In Ring Rows -- Level 5 (p.420)
Straddle One-Arm Rows -- Level 6 (p.421)
One-Arm Rows -- Level 7 (p.422)

Pull-ups
Jumping Pull-ups -- Level 1 (p.423)
Bar Pull-up Eccentrics -- Level 2 (p.424)
Bar Pull-ups -- Level 3 (p.425)
L-Sit Pull-ups -- Level 4 (p.426)
Pullover -- Level 5 (p.427)

Ring Pull-ups + One-Arm Chin-ups
Rings L-Sit Pull-ups -- Level 4 (p.428)
Rings Wide Grip Pull-ups -- Level 5 (p.429)
Rings Wide Grip L-Sit Pull-ups -- Level 6 (p.429)
Rings Archer Pull-ups -- Level 7 (p.430)
One-Arm Chin-up / Pull-up Eccentrics -- Level 8 (p.431)
One-Arm Chin-up -- Level 9 (p.434)
One-Arm Chin-up +15 lbs. -- Level 10 (p.434)
One-Arm Chin-up +25 lbs. -- Level 11 (p.434)

Weighted Pull-ups
(section intro, no single leveled exercise, p.436)

Explosive Pull-ups
Kipping Pull-ups -- Level 2 (p.437)
Bar Pull-ups -- Level 3 (p.438)
Kipping Clapping Pull-ups -- Level 4 (p.439)
Non-Kipping Clapping Pull-ups -- Level 5 (p.440)
L-Sit Clapping Pull-ups -- Level 6 (p.441)
Kipping, Behind-the-Back Clapping Pull-ups -- Level 7 (p.442)
L-Sit, Slap-the-Abdominals Pull-ups -- Level 8 (p.443)
L-Sit, Slap-the-Thighs Pull-ups -- Level 9 (p.444)
Straight-Body, Slap-the-Thighs Pull-ups -- Level 10 (p.445)
Non-Kipping, Behind-the-Back Clapping Pull-ups -- Level 11 (p.446)

Iron Cross
Iron Cross Progressions -- Level 9 (p.448)
Hold Iron Cross -- Level 10 (p.451)
Iron Cross to Back Lever -- Level 11 (p.452)
Iron Cross Pullouts -- Level 13 (p.453)
Hang Pull to Back Lever -- Level 14 (p.454)
Butterfly Mount -- Level 15 (p.455)
Support Hold to Hang to Iron Cross -- Level 16 (p.456)

CHAPTER 26: PUSHING VARIATIONS

Planche -- Parallel Bars and Floor
Frog Stand -- Level 3 (p.458)
Straight-Arm Frog Stand -- Level 4 (p.459)
Tuck Planche -- Level 5 (p.460)
Advanced Tuck Planche -- Level 6 (p.461)
Pseudo Planche Pushups -- Level N/A (p.462)
Band-Assisted Planche -- Level N/A (p.463)
Straddle Planche -- Level 8 (p.464)
Half Layout / One-Leg-Out Planche -- Level 9 (p.465)
Full Planche -- Level 11 (p.466)
Straight-Arm Straddle Planche to Handstand -- Level 12 (p.467)
Rings Straight-Arm Straddle Planche to Handstand -- Level 14 (p.468)
Straight-Arm, Straight-Body from Planche to Handstand -- Level 15 (p.469)
Rings Straight-Arm, Straight-Body Press to Handstand -- Level 16 (p.470)
Rings Straight-Arm, Straight-Body from Planche to Handstand -- Level 16 (p.471)

Rings Planche
Rings Frog Stand -- Level 4 (p.472)
Rings Straight-Arm Frog Stand -- Level 5 (p.473)
Rings Tuck Planche -- Level 6 (p.474)
Rings Advanced Tuck Planche -- Level 8 (p.475)
Rings Straddle Planche -- Level 10 (p.476)
Rings Half Layout / One-Leg-Out Planche -- Level 12 (p.477)
Rings Full Planche -- Level 14 (p.477)

Planche Pushups -- Parallel Bars and Floor
Tuck Planche Pushups -- Level 6 (p.479)
Advanced Tuck Planche Pushups -- Level 8 (p.480)
Straddle Planche Pushups -- Level 10 (p.480)
Half Layout / One-Leg-Out Planche Pushups -- Level 12 (p.481)
Full Planche Pushups -- Level 14 (p.482)

Rings Planche Pushups
Rings Tuck Planche Pushups -- Level 8 (p.483)
Rings Advanced Tuck Planche Pushups -- Level 10 (p.483)
Rings Straddle Planche Pushups -- Level 12 (p.483)
Rings Half Layout / One-Leg-Out Planche Pushups -- Level 14 (p.484)
Rings Full Planche Pushups -- Level 16 (p.484)

Pushups
Standard Pushups -- Level 1 (p.485)
Diamond Pushups -- Level 2 (p.486)
Rings Wide Pushups -- Level 3 (p.486)
Rings Pushups -- Level 4 (p.487)
Rings-Turned-Out Pushups -- Level 5 (p.488)
Rings-Turned-Out Archer Pushups -- Level 6 (p.489)
Rings-Turned-Out, 40-Degree-Lean Pseudo Planche Pushups -- Level 7 (p.490)
Rings-Turned-Out, 60-Degree-Lean Pseudo Planche Pushups -- Level 8 (p.491)
Rings-Turned-Out Maltese Pushups -- Level 9 (p.492)
Wall Pseudo Planche Pushups -- Level 10 (p.493)
Rings Wall Pseudo Planche Pushups -- Level 11 (p.494)
Wall Maltese Pushups -- Level 12 (p.495)
Rings Wall Maltese Pushups -- Level 13 (p.496)
Clapping Pushup Variations -- Level N/A (p.497)

One-Arm Pushups
Hands-Elevated, One-Arm Pushup -- Level 5 (p.499)
Straddle One-Arm Pushup -- Level 6 (p.501)
Rings Straddle One-Arm Pushup -- Level 7 (p.502)
Straight-Body, One-Arm Pushup -- Level 8 (p.503)
Rings Straight-Body, One-Arm Pushup -- Level 9 (p.504)

Dips
Parallel Bar Jumping Dips -- Level 1 (p.505)
Parallel Bar Dip Eccentrics -- Level 2 (p.506)
Parallel Bar Dips -- Level 3 (p.507)
L-Sit Dips -- Level 4 (p.508)
45-Degree Forward-Lean Dips -- Level 5 (p.509)
One-Arm Dip -- Levels 8 & 9 (p.510)

Rings Dips
Support Hold -- Level 1 (p.512)
Rings-Turned-Out Support Hold -- Level 2 (p.513)
Rings Dip Eccentrics -- Level 3 (p.514)
Rings Dips -- Level 4 (p.515)
Rings L-Sit Dips -- Level 5 (p.516)
Rings Wide Dips -- Level 6 (p.517)
Rings-Turned-Out Dip Variations -- Level N/A (p.518)
Maltese Hold -- Level 17 (p.520)

Weighted Dips
(section intro, no single leveled exercise, p.521)

CHAPTER 27: MULTI-PLANE EXERCISES, CORE, AND LEGS

Muscle-ups and Inverted Muscle-ups
Muscle-up Negatives -- Level 3 (p.525)
Kipping Muscle-ups -- Level 4 (p.526)
Muscle-ups -- Level 5 (p.527)
Wide / No-False-Grip Muscle-ups -- Level 6 (p.528)
Strict Bar Muscle-Ups -- Level 7 (p.529)
Straddle Front Lever to Muscle-up to Advanced Tuck Planche -- Level 8 (p.530)
L-Sit Muscle-up -- Level 8 (p.531)
One-Arm-Straight Muscle-up -- Level 9 (p.532)
Felge Backward, Straight-Body to Support -- Level 10 (p.533)
Front Lever Muscle-up to Straddle Planche -- Level 11 (p.534)
Felge Backward, Straight-Body to Handstand -- Level 12 (p.535)
Straight-Body Rotation to Handstand -- Level 14 (p.536)
Butterfly Mount -- Level 15 (p.536)
Elevator / Inverted Muscle-up to Handstand -- Level 17 (p.538)

Elbow Levers
Two-Arm Elbow Lever -- Level 5 (p.539)
Rings Two-Arm Elbow Lever -- Level 6 (p.540)
One-Arm Straddle Elbow Lever -- Level 7 (p.541)
One-Arm, Straight-Body Elbow Lever -- Level 8 (p.542)

Flags
(section, p.543, no leveled list captured in index)

Ab Wheel
25s Plank -- Level 2 (p.545)
60s Plank -- Level 3 (p.545)
One-Arm, One-Leg Plank -- Level 4 (p.545)
The Plank Position -- (p.545, no level)
Knees Ab Wheel -- Level 5 (p.546)
Ramp Ab Wheel -- Level 6 (p.546)
Ab Wheel Eccentrics -- Level 7 (p.546)
Full Ab Wheel -- Level 8 (p.546)
Ab Wheel + 20 lbs. -- Level 9 (p.546)
One-Arm Ab Wheel -- Level 10 (p.546)

Specific Rings Elements (this is a summary/cross-reference section
listing levels of exercises already defined elsewhere -- consider
skipping to avoid duplicate rows, or use only for cross-checking)
Rings-Turned-Out L-Sit -- Level 5 (p.549)
Rings-Turned-Out Straddle L-Sit -- Level 6 (p.549)
Back Lever -- Level 7 (p.549)
Front Lever -- Level 8 (p.549)
Rings 90-Degree V-Sit -- Level 9 (p.550)
Iron Cross / Straddle Planche -- Level 10 (p.550)
Full Planche -- Level 14 (p.550)
Inverted Cross -- Level 16 (p.550)

Rings Kipping Skills
Kip to Support -- Level 6 (p.551)
Back Kip to Support -- Level 7 (p.553)
Straight-Arm Kip to L-Sit -- Level 9 (p.554)
Straight-Arm Back Kip to Support -- Level 10 (p.555)
Back Kip to Handstand -- Level 11 (p.556)
Straight-Arm Kip to V-Sit / Kip to Cross or L-Sit Cross -- Level 13 (p.557)
Back Kip to Cross or L-Sit Cross -- Level 14 (p.558)
Back Kip to Straddle Planche -- Level 15 (p.559)

Rings Felge Skills
Felge Forward to Support (Piked Body) -- Level 6 (p.561)
Felge Backward to Support (Piked Body) -- Level 7 (p.562)
Felge Forward to Support (Straight Body) -- Level 9 (p.563)
Felge Backward to Support (Straight Body) -- Level 10 (p.564)
Felge Backward to Handstand (Straight Body) -- Level 12 (p.565)
Felge Forward to Cross (Straight-Arm, Bent Body) -- Level 13 (p.566)
Felge Forward to Straddle Planche (Straight-Arm) -- Level 14 (p.567)
Felge Forward to Handstand (Straight-Arm, Straight-Body) -- Level 15 (p.568)

Squats
Asian Squat -- Level N/A (p.569)
Parallel Squat -- Level 1 (p.570)
Full Squat -- Level 2 (p.571)
Side-to-Side Squat -- Level 3 (p.572)
Pistols (Single-Leg Squats) -- Level 4 (p.573)
Weighted Pistols -- Levels 5+ (p.575)

Other Leg Exercises -- (p.576, no single leveled list captured)
Miscellaneous Exercises -- (p.579, no single leveled list captured)

=== RAW INDEX TEXT END ===
