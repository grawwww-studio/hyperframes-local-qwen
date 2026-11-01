#!/usr/bin/env bash
# Start llama.cpp's server with the stock Qwen3.8-27B, run the briefs through runner.py, stop the server.
#   MODEL=/path/to/Qwen3.8-27B-Q4_K_M.gguf ./run.sh B1 B2 B3 B4 B5            thinking off, results in runs_nothink/
#   THINK=1 MODEL=/path/to/Qwen3.8-27B-Q4_K_M.gguf ./run.sh B1 B2 B3 B4 B5    thinking on, results in runs/
# Optional: LLAMA_SERVER (path to llama-server), QHOST, QPORT, SEED (a number), HF_CMD (how to call HyperFrames).
set -uo pipefail
D="$(cd "$(dirname "$0")" && pwd)"
: "${MODEL:?set MODEL to the Q4_K_M .gguf file}"
export QHOST="${QHOST:-localhost}" QPORT="${QPORT:-8080}"
"${LLAMA_SERVER:-llama-server}" -m "$MODEL" --host "$QHOST" --port "$QPORT" -c 32768 -ngl 99 -fa on --cache-type-k q8_0 --cache-type-v q8_0 --parallel 1 --threads 4 --jinja --no-webui > "$D/llama-server.log" 2>&1 &
LP=$!
trap 'kill $LP 2>/dev/null; wait $LP 2>/dev/null' EXIT
until curl -sf -m 2 "http://$QHOST:$QPORT/health" > /dev/null 2>&1; do kill -0 $LP 2>/dev/null || { echo "server died, see llama-server.log"; exit 1; }; sleep 3; done
echo "server up $(date -u +%T)"
if [ -n "${THINK:-}" ]; then python3 "$D/runner.py" "$@"; else NOTHINK=1 RUNS=runs_nothink python3 "$D/runner.py" "$@"; fi
echo "done $(date -u +%T)"
