TOP=../..

include $(TOP)/configure/CONFIG
-include $(TOP)/configure/CONFIG.PyDevice

PROD_IOC = plotApp
DBD += plotApp.dbd

plotApp_DBD += base.dbd
plotApp_DBD += pydev.dbd
plotApp_DBD += pycalcRecord.dbd

plotApp_LIBS += pydev
plotApp_SRCS += plotApp_registerRecordDeviceDriver.cpp
plotApp_SRCS_DEFAULT += main.cpp
plotApp_SRCS_vxWorks += -nil-
plotApp_LIBS += $(EPICS_BASE_IOC_LIBS)

include $(TOP)/configure/RULES
