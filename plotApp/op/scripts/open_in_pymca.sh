#!/usr/bin/env bash
# Open the IOC's current scan file in PyMca (Phase 6: peak fit / rich overlay).
# Usage: open_in_pymca.sh [EPICS_PREFIX]
# Default prefix: TAS:Plot:
set -euo pipefail

PREFIX="${1:-TAS:Plot:}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PATH_FILE="$(caget -s "${PREFIX}FullFileName_RBV.$" 2>/dev/null || true)"
if [[ -z "${PATH_FILE}" || ! -f "${PATH_FILE}" ]]; then
    PATH_FILE="$(caget -s "${PREFIX}SelectedFile.$" 2>/dev/null || true)"
fi

if [[ -z "${PATH_FILE}" || ! -f "${PATH_FILE}" ]]; then
    echo "open_in_pymca: no readable file at ${PREFIX}FullFileName_RBV.$ / SelectedFile.$" >&2
    exit 1
fi

exec python3 "${SCRIPT_DIR}/open_in_pymca.py" "${PATH_FILE}"
