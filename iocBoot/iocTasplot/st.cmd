# Example startup for ioc-tasplot PyDevice IOC
# Deploy under /epics/iocs/ioc-tasplot; adjust paths like ioc-hkl.

epicsEnvSet("TOP", "/epics/iocs/ioc-tasplot")
epicsEnvSet("PYDEVICE", "/epics/support/pydevice/main")

# Python: tasplot + graffiti_app (this repository)
epicsEnvSet("PYTHONPATH", "$(TOP)/python")
epicsEnvSet("PYTHONPATH", "$(PYTHONPATH):$(TOP)")

cd "${TOP}"

## Register PyDevice (see ioc-hkl / ioc-pymca Makefiles for link lines)
# dbLoadDatabase("$(PYDEVICE)/dbd/pydev.dbd")
# plotApp_registerRecordDeviceDriver pdb

pydev("from graffiti_app import graffiti_plot")

## Optional defaults for HB3 archive development tree
pydev("graffiti_plot.set_file_path('/home/kg1/Documents/Detector/HB3/HB3_data/User/exp382/Datafiles')")
pydev("graffiti_plot.set_file_name('HB3_exp0382_scan')")
pydev("graffiti_plot.set_file_number(1)")

dbLoadTemplate("plotApp/Db/plot.substitutions")

iocInit()

# caput HB3:Plot:Acquire 1
# caget HB3:Plot:Xdata
