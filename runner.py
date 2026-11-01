#!/usr/bin/env python3
"""EP05 pilot runner: brief -> local Qwen -> HyperFrames check/render, up to 2 automatic fix rounds. Usage: runner.py B1 [B2 ...]"""
import json, os, re, shutil, subprocess, sys, time, urllib.request
D = os.path.dirname(os.path.abspath(__file__))
URL = "http://%s:%s/v1/chat/completions" % (os.environ.get("QHOST", "localhost"), os.environ.get("QPORT", "8080"))
SYSTEM = open(f"{D}/system.md").read()
BRIEFS = {}
txt = open(f"{D}/briefs.md").read()
for m in re.finditer(r"^## (B\d) (.*?)\n(.*?)(?=^## |\Z)", txt, re.S | re.M):
    BRIEFS[m.group(1)] = (m.group(2), m.group(3).strip())

def chat(messages):
    body = json.dumps({"model": "qwen", "messages": messages, "temperature": 0.6, "top_p": 0.95, "max_tokens": 20000, **({"seed": int(os.environ["SEED"])} if os.environ.get("SEED") else {}), **({"chat_template_kwargs": {"enable_thinking": False}} if os.environ.get("NOTHINK") else {})}).encode()
    t = time.time()
    r = json.load(urllib.request.urlopen(urllib.request.Request(URL, body, {"Content-Type": "application/json"}), timeout=1500))
    return r, time.time() - t

def extract(content):
    m = re.findall(r"```html\s*\n(.*?)```", content, re.S)
    if m: return max(m, key=len)
    m = re.search(r"(<!doctype html>.*</html>)", content, re.S | re.I)
    return m.group(1) if m else None

HF = os.environ.get("HF_CMD", "npx --yes hyperframes@0.8.176").split()
def hf(proj, *args, timeout=600):
    env = dict(os.environ, HYPERFRAMES_NO_TELEMETRY="1", DO_NOT_TRACK="1", PRODUCER_BROWSER_GPU_MODE="software")
    t = time.time()
    p = subprocess.run([*HF, *args], cwd=proj, env=env, capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout + p.stderr), time.time() - t

def check_feedback(out):
    # keep Lint/Runtime/Layout/Motion; contrast is advisory (it flags our own reference example) and is not fed back
    out = re.sub(r"\x1b\[[0-9;]*m", "", out)
    keep, skip = [], False
    for ln in out.splitlines():
        if ln.startswith("Contrast"): skip = True; continue
        if ln.startswith(("Snapshots", "Lint", "Runtime", "Layout", "Motion")): skip = False
        if not skip: keep.append(ln)
    return "\n".join(keep)

def errors_in(fb):
    errs = re.findall(r"^\s+✗ .*$", fb, re.M)
    return errs

def say(*a):
    if os.environ.get("VERBOSE"): print(*a, flush=True)

HINT = json.load(open(os.environ["HINTFILE"])) if os.environ.get("HINTFILE") else None

def run(bid):
    name, brief = BRIEFS[bid]
    out = f"{D}/{os.environ.get('RUNS','runs')}/{bid}"; shutil.rmtree(out, ignore_errors=True)
    proj = f"{out}/project"; shutil.copytree(os.environ.get("TPL", f"{D}/tpl"), proj)
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": f"Brief {bid}: {name}\n\n{brief}\n\nWrite the complete index.html."}]
    if HINT:  # RR2: one human sentence about the frame, one round, no fix rounds
        src = open(f"{D}/{HINT[bid]['source']}").read()
        msgs += [{"role": "assistant", "content": "```html\n" + src + "\n```"}, {"role": "user", "content": "A person watched the rendered video and says: " + HINT[bid]["sentence"] + "\n\nReply with the complete corrected index.html in one ```html block."}]
    log = {"brief": bid, "name": name, "rounds": [], "model": "Qwen3.8-27B-Q4_K_M stock"}
    t_llm = tok_in = tok_out = 0
    ok = False
    for rnd in range(1 if HINT else 3):  # 0 = first draft, 1-2 = fix rounds
        say(f"[{bid}] round {rnd}: asking the model ...")
        r, dt = chat(msgs)
        msg = r["choices"][0]["message"]; content = msg.get("content") or ""
        u = r["usage"]; t_llm += dt; tok_in += u["prompt_tokens"]; tok_out += u["completion_tokens"]
        open(f"{out}/llm_round{rnd}.txt", "w").write((msg.get("reasoning_content") or "") and "[REASONING]\n" + msg["reasoning_content"] + "\n[CONTENT]\n" + content or content)
        html = extract(content)
        rec = {"round": rnd, "llm_s": round(dt, 1), "prompt_tokens": u["prompt_tokens"], "completion_tokens": u["completion_tokens"], "finish": r["choices"][0]["finish_reason"]}
        if not html:
            rec["error"] = "no html block"; log["rounds"].append(rec)
            msgs += [{"role": "assistant", "content": content[:4000]}, {"role": "user", "content": "No ```html block found. Reply with the complete index.html in one ```html block."}]
            continue
        open(f"{proj}/index.html", "w").write(html); open(f"{out}/index_round{rnd}.html", "w").write(html)
        say(f"[{bid}] round {rnd}: {r['usage']['completion_tokens']} tokens in {dt:.0f} s; hf check ...")
        rc, o, ct = hf(proj, "check", "--no-browser-gpu")
        fb = check_feedback(o); errs = errors_in(fb); rec["check_s"] = round(ct, 1); rec["check_errors"] = errs
        err_text = None
        say(f"[{bid}] round {rnd}: check errors: {len(errs)}" + "".join("\n    " + e.strip()[:110] for e in errs))
        if errs or "never ran" in o:
            err_text = "hyperframes check reported errors:\n" + fb[:3500]
        else:
            t0 = time.time(); rc, o2, rt = hf(proj, "render", "-o", f"{out}/{bid}.mp4", "--fps", "24", "--no-browser-gpu", "--workers", "4")
            rec["render_s"] = round(rt, 1)
            if rc != 0 or not os.path.exists(f"{out}/{bid}.mp4"):
                err_text = "hyperframes render failed:\n" + re.sub(r"\x1b\[[0-9;]*m", "", o2)[-3000:]
            else:
                ok = True
        log["rounds"].append(rec)
        say(f"[{bid}] round {rnd}: " + ("render ok" if ok else "needs a fix round"))
        if ok or HINT: break
        if rnd < 2:
            msgs += [{"role": "assistant", "content": content}, {"role": "user", "content": err_text + "\n\nFix these errors and reply with the complete corrected index.html in one ```html block."}]
    log.update(render_ok=ok, fix_rounds=len(log["rounds"]) - 1, llm_s=round(t_llm, 1), prompt_tokens=tok_in, completion_tokens=tok_out)
    json.dump(log, open(f"{out}/log.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in log.items() if k != "rounds"}), flush=True)

for b in sys.argv[1:]: run(b)
