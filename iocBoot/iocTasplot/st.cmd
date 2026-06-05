#!../../bin/linux-x86_64/plotApp

< envPaths

epicsEnvSet("IOC", "iocTasplot")
epicsEnvSet("PREFIX", "TAS:Plot:")

# tasplot package + graffiti_app (repository root on PYTHONPATH)
epicsEnvSet("PYTHONPATH", "$(TOP)/python")
epicsEnvSet("PYTHONPATH", "$(PYTHONPATH):$(TOP)")

cd "${TOP}"

dbLoadDatabase "${TOP}/dbd/plotApp.dbd"
plotApp_registerRecordDeviceDriver pdbbase

dbLoadTemplate("$(TOP)/db/plot.substitutions")

cd "${TOP}/iocBoot/${IOC}"

pydev("from graffiti_app import graffiti_plot")

## Development defaults (override via caput or edit)
pydev("graffiti_plot.set_file_path('/home/kg1/Documents/Detector/HB3/HB3_data/User/exp382/Datafiles')")
pydev("graffiti_plot.set_file_name('HB3_exp0382_scan')")
pydev("graffiti_plot.set_file_number(1)")

iocInit

## Smoke test after boot (PREFIX from epicsEnvSet above):
## caput TAS:Plot:Acquire 1
## caget TAS:Plot:NRows_RBV
