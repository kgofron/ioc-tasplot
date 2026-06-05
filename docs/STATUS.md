# ioc-tasplot — session checkpoint (2026-06-04)

Handoff for resuming work after a break.

## Repository

- **Remote:** https://github.com/kgofron/ioc-tasplot
- **Branch:** `main` (in sync with `origin/main` at last check)
- **Latest commits:**
  - `6dcaff1` chore(iocBoot): make st.cmd executable for shebang launch
  - `c9f961e` fix(build): CONFIG.PyDevice via CONFIGS (ioc-hkl lifecycle)
  - `914aa41` ci: pytest workflow; docs: build and boot steps
  - `97db810` feat(build): EPICS PyDevice IOC build
  - `1556aed` feat: tasplot parsers, PyDevice backend, IOC skeleton

## Build

```bash
cd /home/kg1/Documents/src/github/ioc-tasplot
cp configure/RELEASE.local.example configure/RELEASE.local   # once
make -sj
```

- Requires: EPICS Base (`/epics/base`), `python3-dev`
- `configure/CONFIG.PyDevice` is **generated** on build, **removed** on `make clean uninstall` (gitignored)

## IOC runtime

**Not running** when this file was written.

**Start:**

```bash
cd iocBoot/iocTasplot
./st.cmd
# or: ../../bin/linux-x86_64/plotApp st.cmd
```

**PV prefix:** `TAS:Plot:` (`PREFIX` in `st.cmd`; 18 records — see `dbl` after `iocInit`)

**Dev defaults in st.cmd:** HB3 exp382 scan 1 under  
`/home/kg1/Documents/Detector/HB3/HB3_data/User/exp382/Datafiles`

**Smoke test (second terminal):**

```bash
caput TAS:Plot:Acquire 1
caget TAS:Plot:NRows_RBV
caget TAS:Plot:FullFileName_RBV
caget TAS:Plot:LastError_RBV
```

## Tests

```bash
PYTHONPATH=. python3 -m pytest -q   # 13 passed
```

GitHub Actions: `.github/workflows/test.yml` on push/PR.

## Done

- [x] `tasplot` SPiCE + SPEC parsers + fixtures
- [x] `graffiti_app` PyDevice engine
- [x] `plotApp` DB templates + boot
- [x] Full EPICS build (vendored PyDevice in `src/`)
- [x] IOC boots; `iocInit` completes
- [x] CI + README build instructions

## Next (in order)

1. **Runtime validation** — `caput`/`caget` with real `.dat` / SPEC file
2. **Phoebus** — open `plotApp/op/bob/TASPlot.bob`; **Acquire**; verify XY plot
3. **Beamline deploy** — `/epics/iocs/ioc-tasplot`, production `st.cmd`, autosave
4. **Live reload** — periodic `Acquire` or inotify while scan grows
5. **Facility** — PVXS/QSRV 2; fits / column picker (Graffiti parity)

## Notes

- Old Graffiti C IOC still at `Detector/HB3/applications/hb3-Graffiti` (separate tree)
- SPiCE / pcaspy screenshots on disk may help Phoebus layout (optional)
- Fine-grained GitHub PAT needs **Contents** + **Workflows** for push
