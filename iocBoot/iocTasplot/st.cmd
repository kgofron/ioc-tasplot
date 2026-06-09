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
pydev("graffiti_plot.set_selected_file('/home/kg1/Documents/Detector/HB3/HB3_data/User/exp382/Datafiles/HB3_exp0382_scan0001.dat')")

## Dedicated CA TCP port (avoid collision with other local IOCs on 5064/44029)
#epicsEnvSet("EPICS_CAS_SERVER_PORT", "50950")
## Single beacon address (avoids Phoebus "multiple servers" on VPN + LAN)
#epicsEnvSet("EPICS_CAS_BEACON_ADDR_LIST", "10.1.232.74")

iocInit

## Sync spinner after pydev boot (path comes from set_selected_file + SelectedFilePath scan)
dbpf("TAS:Plot:FileNumber", "1")

## Smoke test after boot (PREFIX from epicsEnvSet above):
## caget TAS:Plot:NRows_RBV
## caget -S TAS:Plot:SelectedFile.VAL$
## caget -S TAS:Plot:FullFileName_RBV.VAL$
