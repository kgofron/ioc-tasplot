# Local demo data (not tracked)

Put writable scan files here for instrument demos (Live reload, Overlay).

| File | Purpose |
|------|---------|
| [`ADR-scan-formats.md`](ADR-scan-formats.md) | **Tracked** — SPEC vs SPiCE cheat sheet + ADRs (EOL / migration) for demos |
| `live_test.dat` | Growing-scan Live demo (HB3 exp382 scan0001 + extra points) |
| `yongcai_20240530.spec` | CERTIF SPEC multi-scan demo (from PyMCA/YongCai/20240530) |

```bash
# After clone / before Monday talk
cp /tmp/live_test.dat demo/live_test.dat   # or refresh from HB3 archive
# SPEC (optional refresh):
# cp /home/kg1/Documents/src/PyMCA/YongCai/20240530 demo/yongcai_20240530.spec

# Phoebus / IOC:
#   …/ioc-tasplot/demo/live_test.dat          — Live checkbox + append/touch
#   …/ioc-tasplot/demo/yongcai_20240530.spec  — SPEC #S spinner for multi-scan
```

Scan `.dat` / `.spec` under `demo/` are **gitignored**. Markdown ADRs (`demo/ADR*.md`) and this README are **tracked** (GitHub-friendly).
