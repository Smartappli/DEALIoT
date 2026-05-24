#!/usr/bin/env bash
set -euo pipefail

decoder_home="${WILDFI_DECODER_HOME:-/opt/wildfi-decoder}"
workdir="${WILDFI_DECODER_WORKDIR:-/work}"
mode="${WILDFI_DECODER_MODE:-2}"

cd "$workdir"

if [[ -n "${WILDFI_DECODER_RAW_INPUT:-}" ]]; then
  printf '%b' "$WILDFI_DECODER_RAW_INPUT" | java -jar "${decoder_home}/WildFiDecoderStandalone.jar"
  exit 0
fi

case "$mode" in
  1 | 2)
    printf '%s\n%s\n%s\n%s\n%s\n\n99\n' \
      "$mode" \
      "${WILDFI_DECODER_BURST_FORM:-0}" \
      "${WILDFI_DECODER_FILE_INDEX:-0}" \
      "${WILDFI_DECODER_TAG_SELECTION:-0}" \
      "${WILDFI_IMU_FREQUENCY:-25}" \
      | java -jar "${decoder_home}/WildFiDecoderStandalone.jar"
    ;;
  3 | 4 | 5 | 6 | 7 | 8)
    printf '%s\n\n99\n' "$mode" | java -jar "${decoder_home}/WildFiDecoderStandalone.jar"
    ;;
  *)
    echo "Unsupported WILDFI_DECODER_MODE=$mode. Use 1, 2, 3, 4, 5, 6, 7, 8 or WILDFI_DECODER_RAW_INPUT." >&2
    exit 64
    ;;
esac
