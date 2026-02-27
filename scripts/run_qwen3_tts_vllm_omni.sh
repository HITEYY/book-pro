#!/usr/bin/env bash
set -euo pipefail

# Defaults are selected for local development.
MODEL="${QWEN3_TTS_MODEL:-Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice}"
HOST="${QWEN3_TTS_HOST:-0.0.0.0}"
PORT="${QWEN3_TTS_PORT:-8091}"
STAGE_CONFIGS_PATH="${QWEN3_TTS_STAGE_CONFIGS_PATH:-}"

if [[ -z "${STAGE_CONFIGS_PATH}" ]]; then
  STAGE_CONFIGS_PATH="$(
    python - <<'PY'
from pathlib import Path
import importlib.util

spec = importlib.util.find_spec("vllm_omni")
if not spec or not spec.origin:
    raise SystemExit(0)

candidate = Path(spec.origin).resolve().parent / "model_executor" / "stage_configs" / "qwen3_tts.yaml"
if candidate.exists():
    print(candidate)
PY
  )"
fi

if [[ -z "${STAGE_CONFIGS_PATH}" ]]; then
  echo "qwen3_tts.yaml 경로를 찾지 못했습니다."
  echo "QWEN3_TTS_STAGE_CONFIGS_PATH를 설정하거나 vllm-omni 설치를 확인하세요."
  exit 1
fi

echo "Starting vLLM-Omni Qwen3-TTS server"
echo "MODEL=${MODEL}"
echo "HOST=${HOST}"
echo "PORT=${PORT}"
echo "STAGE_CONFIGS_PATH=${STAGE_CONFIGS_PATH}"

exec vllm serve "${MODEL}" \
  --stage-configs-path "${STAGE_CONFIGS_PATH}" \
  --omni \
  --host "${HOST}" \
  --port "${PORT}" \
  --trust-remote-code \
  --enforce-eager
