# EP05 pilot: briefs and pass rules (written 2026-10-27 before any run)

Setup: stock Qwen3.8-27B Q4_K_M (ggml-org), local llama-server, HyperFrames 0.8.176 (pinned, CPU render). All briefs 1920x1080, 24 fps,
Grawwww identity C dark (paper #0E0E0E, ink #F4F4F1, cyan #12A9E6, magenta #FF2D92, yellow #FFD400 only as a band behind #111 text;
fonts Anybody / Schibsted Grotesk / Spline Sans Mono; no rounded corners, shadows or gradients). No third-party logos, no client names.
Own assets available to briefs: `assets/logo-negative.png`, `assets/icon.svg` (brand kit).

## B1 Title card with kinetic type (5 s)
Title "Local AI, real video" in huge uppercase display type, words slide/stagger in one by one; the word "real" gets a yellow marker band that
wipes in from the left. Small mono eyebrow "EP05 / Experiment" above, a thin rule that draws across below. Hold for the last second.

## B2 Three-step explainer with icons (9 s)
Heading "How it works". Three columns, each with a number (01/02/03), a simple inline-SVG icon drawn by the model (no external icon files)
and a label: "Write a brief" (pencil/document), "Model writes the code" (brackets </>), "Render the video" (play triangle). Steps reveal
sequentially with connector lines between them.

## B3 Chart reveal from small JSON (8 s)
Data (use exactly): {"title":"Render time per card (s)","unit":"s","rows":[{"label":"Title","value":42},{"label":"Explainer","value":58},{"label":"Chart","value":51},{"label":"Lower third","value":23}]}.
Horizontal bars, cyan, growing from zero with staggered timing, value labels counting up or fading in at the bar end, the largest bar
highlighted by a yellow band behind its value. Chart title from the JSON. Bars must be proportional to the values.

## B4 Lower third (4 s, transparent-looking over a dark plate)
A lower third at bottom-left over a plain dark gradient-free plate: name "Lara Quinn" (display type), role line "Presenter, Grawwww" (mono),
cyan accent bar that wipes in first, then text slides in, hold, then everything wipes out in the last 0.5 s.

## B5 Product teaser with own assets (10 s)
10 s teaser for "Grawwww Studio: local AI, delivered". Use `assets/logo-negative.png` (centre, appears at the end) and `assets/icon.svg`.
Beat sheet: 0-3 s three short lines slam in ("Agents." "Automations." "Video."), 3-7 s a row of three feature chips
("Runs on your hardware", "No per-token bill", "Your data stays put") staggered, 7-10 s everything clears and the logo fades/scales in with
the tagline "Local AI, delivered." under it.

## Pass rules (fixed before running)
A brief PASSES only if all of R1-R3 hold; R4 is recorded, not gating.
- R1 Renders: `hf lint`/`check` reports 0 errors and `hf render` exits 0 with an mp4 1920x1080 whose duration is within 0.3 s of the brief.
- R2 Matches brief: every named element is on screen at some point with the exact text/data given, the order/timing beats are followed
  (checked on 6 frames spread over the clip, viewed by the builder), bars proportional in B3.
- R3 No broken layout: no text clipped, overflowing or overlapping other text, nothing off-canvas at the hold frame, contrast readable,
  brand rules respected (no rounded corners/shadows/gradients, yellow only as a band).
- R4 Time: tokens, LLM seconds, fix rounds (max 2 automatic, each feeding back lint/render error text only, no human hints), render seconds.
Fix rounds are automatic and only for errors from `hf check` / render; layout flaws seen by eye are NOT fed back (they count as R3 fail),
so the pass rate is the model's unaided rate with error recovery.
Pass-rate caveat: written for the first pilot (n=5, one run per brief, temperature 0.6); later runs added four per brief with thinking off. Indicative only.
