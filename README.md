# A local Qwen 3.8 27B writes HyperFrames videos: the files behind the episode

The system prompt, the loop script, the five briefs and the two reviewer sentences from the video "HyperFrames with a local Qwen 3.8 27B: 9 of 20 Runs Passed (Thinking Off)".

- Video: VIDEO_URL_SLOT
- Write-up with the results table and the setup notes: https://grawwww.xyz/en/teams/hyperframes-local-qwen/

Everything we used for the Qwen runs, except the model, the logo and icon, the fonts and GSAP (not shared here; see `NOTICE.md`).
The presenter in the video, Lara, is fictional and AI-generated; no real person appears.

## What is here
| File | What it is |
|---|---|
| `system.md` | The one system prompt: file layout, the animation rules the checker enforces, our colours and fonts, one working example. |
| `briefs.md` | The five briefs (B1 title, B2 explainer, B3 chart, B4 lower third, B5 teaser) and the pass rules R1-R3, written before the first run. |
| `runner.py` | The loop, under a hundred lines: brief -> model -> `check` -> render, error text back to the model, two retries at most. |
| `run.sh` | Starts llama.cpp's server with the settings below, runs `runner.py`, stops the server. |
| `contact.sh` | The six-frame contact sheet (five frames spread over the clip, plus the last one) we judged every render on. |
| `hints.json`, `hint-B1.html`, `hint-B3.html` | The reviewer's two sentences and the pages they were sent back with (one round, no fix rounds). |
| `gw.css` | The stylesheet the example in `system.md` links: brand colour variables, font faces and the helper classes `a`, `h`, `m`, `hl`. |

## Set it up
Get the files: `git clone https://github.com/grawwww-studio/hyperframes-local-qwen.git`, then work inside that folder.

1. **Model.** Download `Qwen3.8-27B-Q4_K_M.gguf` from the ggml-org page on Hugging Face (about 19 GB) and check it:
   `sha256sum Qwen3.8-27B-Q4_K_M.gguf` should print `c600de0300ae8a0eb3a6c0b8b5561b8b96f16bd2c863c2a66c42de29d391a747`.
2. **llama.cpp.** Any recent build with `llama-server`. `run.sh` starts it with `-ngl 99 -c 32768 -fa on --cache-type-k q8_0 --cache-type-v q8_0 --jinja` (the whole model on the GPU, a 32,768-token context, flash attention, an 8-bit cache), plus `--parallel 1 --threads 4 --no-webui`. We ran it on one RTX 4090; it peaked at about 21 GB of video memory.
3. **HyperFrames project skeleton.** Create a folder `tpl/` next to `runner.py`; `runner.py` copies it for every run and the model's `index.html` goes into the copy:
   ```
   tpl/meta.json              { "id": "qwen-pilot", "name": "Qwen pilot" }
   tpl/lib/gw.css             the file in this repository
   tpl/vendor/gsap.min.js     from the gsap package (we used 3.14.2)
   tpl/fonts/                 anybody-latin-wdth-normal.woff2, schibsted-grotesk-latin-wght-normal.woff2, spline-sans-mono-latin-wght-normal.woff2
   tpl/assets/                logo-negative.png and icon.svg: put your own here (brief B5 uses them)
   ```
   Node.js is needed. `runner.py` calls `npx --yes hyperframes@0.8.176` (pinned: a newer release came out two hours after ours). To call HyperFrames another way, set `HF_CMD`. We rendered on the CPU (`--no-browser-gpu`) with telemetry off.
4. **Run.**
   ```
   MODEL=/path/to/Qwen3.8-27B-Q4_K_M.gguf ./run.sh B1 B2 B3 B4 B5
   ```
   Thinking is switched off per request (`chat_template_kwargs: {"enable_thinking": false}`); `THINK=1` leaves it on. Each run leaves `runs_nothink/Bn/` (or `runs/Bn/`) with `index_round*.html`, `llm_round*.txt`, `log.json` and `Bn.mp4`.
5. **Look at it.** `./contact.sh runs_nothink/B1/B1.mp4 sheet.png`, then judge the sheet against the pass rules in `briefs.md`. The checker cannot do that step.

## Settings we used
Temperature 0.6, top_p 0.95, `max_tokens` 20000, 1920x1080 at 24 fps, HyperFrames 0.8.176. Seeds 1-3 for the repeat runs: `SEED=1 NOTHINK=1 RUNS=runs_nothink_s1 python3 runner.py B1 ...` (the first run of each brief was unseeded).
The reviewer-sentence test: `HINTFILE=hints.json SEED=1 NOTHINK=1 RUNS=hint_s1 python3 runner.py B1 B3` (three seeds, one round, no fix rounds).

## What we got, so you know what to expect
Thinking off, four runs per brief: lower third 3 of 4, explainer 2, teaser 2, chart 1, title 1: **9 of 20** passed our rules. Thinking on, one run per brief: 3 of 5 (the chart never arrived: three answers of 20,000 tokens with no HTML). Claude Sonnet 5.5 on the same briefs, one run each: 5 of 5. Judged by eye on six frames per run by AI reviewers (9 of 20 and 10 of 20; we kept the stricter). A small sample: a first look, not a benchmark. Full write-up: the link at the top.

## Licences
Our files here are MIT (see LICENSE; NOTICE.md says exactly which files that covers). Qwen's own 27B release is Apache-2.0, llama.cpp is MIT and HyperFrames is Apache-2.0; third-party notices are in `NOTICE.md`. This is a test setup for our write-up, not a product.

Not affiliated with HeyGen, the Qwen team or Anthropic.
