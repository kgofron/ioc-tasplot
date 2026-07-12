#!/usr/bin/env bash
# Open the IOC's current scan file in PyMca (Phase 6: peak fit / rich overlay).
# Usage: open_in_pymca.sh [EPICS_PREFIX]
# Default prefix: TAS:Plot:
#
# Phoebus action buttons often hide stderr — failures also go to:
#   /tmp/open_in_pymca.log
set -euo pipefail

PREFIX="${1:-TAS:Plot:}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="${TMPDIR:-/tmp}/open_in_pymca.log"

# File-only by default: Phoebus treats any stderr as WARNING.
log() { printf '%s %s\n' "$(date -Is)" "$*" >>"$LOG"; }
log_err() { printf '%s %s\n' "$(date -Is)" "$*" | tee -a "$LOG" >&2; }

# Ubuntu apt PyMca is built against NumPy 1.x. A newer NumPy under
# /usr/local (e.g. napari) shadows it and breaks spslut (_ARRAY_API).
_APT_PY="/usr/lib/python3/dist-packages"
if [[ -d "${_APT_PY}/PyMca5" && -d "${_APT_PY}/numpy" ]]; then
    export PYTHONPATH="${_APT_PY}${PYTHONPATH:+:${PYTHONPATH}}"
fi

# tasplot (SPiCE → temp SPEC). Prefer env; else locate checkout with tasplot/.
_find_tasplot_root() {
    local cand
    for cand in \
        "${IOC_TASPLOT_ROOT:-}" \
        "${TASPLOT_ROOT:-}" \
        "${SCRIPT_DIR}/../../.." \
        "${HOME}/Documents/src/github/ioc-tasplot" \
        "/home/kg1/Documents/src/github/ioc-tasplot"; do
        [[ -n "${cand}" ]] || continue
        if [[ -f "${cand}/tasplot/__init__.py" ]]; then
            (cd "${cand}" && pwd)
            return 0
        fi
    done
    return 1
}
REPO_ROOT="$(_find_tasplot_root || true)"
if [[ -n "${REPO_ROOT}" ]]; then
    export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}${REPO_ROOT}"
    export IOC_TASPLOT_ROOT="${REPO_ROOT}"
else
    log_err "open_in_pymca: tasplot not found; set IOC_TASPLOT_ROOT to ioc-tasplot checkout"
    exit 1
fi

# Phoebus may not inherit EPICS bin on PATH.
CAGET="$(command -v caget || true)"
if [[ -z "${CAGET}" ]]; then
    for cand in \
        /epics/base/bin/linux-x86_64/caget \
        /usr/local/epics/base/bin/linux-x86_64/caget \
        "${EPICS_BASE:+${EPICS_BASE}/bin/linux-x86_64/caget}"; do
        if [[ -n "${cand}" && -x "${cand}" ]]; then
            CAGET="${cand}"
            break
        fi
    done
fi
if [[ -z "${CAGET}" ]]; then
    log_err "open_in_pymca: caget not found (PATH=${PATH})"
    exit 1
fi

# Long-string CHAR waveforms need -S (not -s). -t = value only.
caget_path() {
    local pv="$1"
    local raw
    raw="$("${CAGET}" -S -t "${pv}" 2>/dev/null || true)"
    # Strip NULs / trailing whitespace from waveform padding.
    raw="$(printf '%s' "${raw}" | tr -d '\0' | sed -e 's/[[:space:]]*$//')"
    printf '%s' "${raw}"
}

PATH_FILE="$(caget_path "${PREFIX}FullFileName_RBV.$")"
if [[ -z "${PATH_FILE}" || ! -f "${PATH_FILE}" ]]; then
    PATH_FILE="$(caget_path "${PREFIX}SelectedFile.$")"
fi

if [[ -z "${PATH_FILE}" || ! -f "${PATH_FILE}" ]]; then
    log_err "open_in_pymca: no readable file (prefix=${PREFIX}). FullFileName/SelectedFile empty or missing."
    exit 1
fi

log "open_in_pymca: opening ${PATH_FILE}"
exec python3 "${SCRIPT_DIR}/open_in_pymca.py" "${PATH_FILE}"
