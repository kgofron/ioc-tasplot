#!../../bin/linux-x86_64/plotApp

< envPaths

epicsEnvSet("IOC", "iocTasplot")

## PV prefix (must match plot.substitutions $(P) and Phoebus macro P).
## Dev default: TAS:Plot:  |  HB3 beamline: HB3:Plot:  (compose as $(BL):Plot: if useful)
epicsEnvSet("P", "TAS:Plot:")
#epicsEnvSet("BL", "HB3")
#epicsEnvSet("P", "$(BL):Plot:")

# tasplot package + graffiti_app (repository root on PYTHONPATH)
epicsEnvSet("PYTHONPATH", "$(TOP)/python")
epicsEnvSet("PYTHONPATH", "$(PYTHONPATH):$(TOP)")

cd "${TOP}"

dbLoadDatabase "${TOP}/dbd/plotApp.dbd"
plotApp_registerRecordDeviceDriver pdbbase

## Expands $(P) from epicsEnvSet above into record names
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

## DataFileText uses I/O Intr (updated on load, not periodic SCAN)
pydev("import pydev; pydev.iointr('data_file_text', graffiti_plot.data_file_text())")

## Sync spinner after pydev boot (uses same P as DB)
dbpf("$(P)FileNumber", "1")

## Smoke test after boot:
## caget $(P)NRows_RBV
## caget -S $(P)SelectedFile.VAL$
## caget -S $(P)FullFileName_RBV.VAL$
