"""
This script initates both the NHR9200 and the Chroma Load and configures them
so that the NHR9200 is operating as a current source charge mode with no
voltage limit and the Chroma is operating as a constant voltage load.

"""
# -----------------------  Labview Test Autppmation modules ------------------
from lta import Lta
import sys
from lta_err import Lta_Error

# python modules imports
import numpy

# ------------------- following code must be in all scripts--------------------
lta = Lta("127.0.0.1", 60100)  # all scripts must create  an Lta object
try:
    lta.connect()  # connect to the Labview Host
    # ---------------------Script code goes here------------------------------------
    Cfg = lta.__get__('FGen.FunctionArbs')
    print(Cfg)

    error = lta.__set__('FGen.FunctionArbs',Cfg)

except Exception as ex:
    err = Lta_Error(ex, sys.exc_info())  # format a labview error
    lta.send_error(err, 3, 'Abort')  # send the error to labview for display
    lta.close()
    print(err)


# The NHRDC is initially set up in operating state: "Charge"  with Voltage Enabled.  This means that it will act as a
# current source and source current until the Voltage Setting has been reached.  The Chroma load is set up as a constant
# voltage load.  To act as a Solar array, the NHRDC voltage control needs to be disabled so the voltage will follow the
# Chroma load acting as an MPPT

# NhrDcConfig['NHRDC']['Modules'][0]['Device(s)Settings']['OutputSettings']['Enable Voltage'] = False
# try:
#     error = lta.__set__('AcPwr.NHRDCPower.SolarArraySim,Config',NhrDcConfig)
# except Exception as ex:
#     err = Lta_Error(ex, sys.exc_info())  # format a labview error
#     lta.send_error(err, 3, 'Abort')  # send the error to labview for display
#     lta.close()
#     print(err)
