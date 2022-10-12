"""
This script initates both the NHR9200 and the Chroma Load and configures them
so that the NHR9200 is operating as a current source charge mode with no
voltage limit and the Chroma is operating as a constant voltage load.

"""
#-----------------------  Labview Test Autppmation modules ------------------
from lta import Lta
import sys
from lta_err import Lta_Error

# ------------------- following code must be in all scripts--------------------
lta = Lta("127.0.0.1", 60100)  # all scripts must create  an Lta object
try:
    lta.connect()  # connect to the Labview Host
    # ---------------------Script code goes here------------------------------------
    ChromaCfg = lta.__get__('AcPwr.ChromaAcLoad.SolarArraySim,Config')
    print(ChromaCfg)
    NhrDcConfig = lta.__get__('AcPwr.NHRDCPower.SolarArraySim,Config')
    print(NhrDcConfig)

# ------------------all scripts should send their errors to labview------------
except Exception as ex:
    err = Lta_Error(ex, sys.exc_info())  # format a labview error
    lta.send_error(err, 3, 'Abort')  # send the error to labview for display
    lta.close()
    print(err)
