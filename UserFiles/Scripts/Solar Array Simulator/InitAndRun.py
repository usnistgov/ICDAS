"""
This script initates both the NHR9200 and the Chroma Load and configures them
so that the NHR9200 is operating as a current source charge mode with no
voltage limit and the Chroma is operating as a constant voltage load.

"""
# -----------------------  Labview Test Autppmation modules ------------------
from lta import Lta
import sys
from lta_err import Lta_Error
from lta_err import LV_to_Py_Error

# python modules imports
import numpy

# a custom exception class
class LtaError(Exception):
    pass

def main():
    # ------------------- following code must be in all scripts--------------------
    lta = Lta("127.0.0.1", 60100)  # all scripts must create  an Lta object
    try:
        lta.connect()  # connect to the Labview Host
    except Exception as ex:
        err = Lta_Error(ex, sys.exc_info())  # format a labview error
        lta.send_error(err, 3, 'Abort')  # send the error to labview for display
        lta.close()
        print(err)


    # The NHRDC is initially set up in operating state: "Charge"  with Voltage Enabled.  This means that it will act as a
    # current source and source current until the Voltage Setting has been reached.  The Chroma load is set up as a constant
    # voltage load.  To act as a Solar array, the NHRDC voltage control needs to be disabled so the voltage will follow the
    # Chroma load acting as an MPPT
    # try:
        # ---------------------Script code goes here------------------------------------
        # ChromaCfg = lta.__get__('AcPwr.ChromaAcLoad.SolarArraySim,Config')
        # print(ChromaCfg)
        # error = lta.__set__('AcPwr.ChromaAcLoad.SolarArraySim,Config', ChromaCfg)


    NhrDcConfig = lta.__get__('AcPwr.NHRDCPower.SolarArraySim,Config')
    #print(NhrDcConfig)
    NhrDcConfig['NHRDC']['Modules'][0]['Device(s)Settings']['OutputSettings']['Enable Voltage'] = False
    error = lta.__set__('AcPwr.NHRDCPower.SolarArraySim,Config', NhrDcConfig)
    error_handler(error)

    ChromaCfg = lta.__get__('AcPwr.ChromaAcLoad.SolarArraySim,Config')
    #print(ChromaCfg)
    ChromaCfg['Device Properties']['Phases'][0]['Config']['Load Voltage (V/Vrms)'] = float(10)
    error = lta.__set__('AcPwr.ChromaAcLoad.SolarArraySim,Config', ChromaCfg)
    error_handler(error)

    # all done
    lta.close

def error_handler(error):
    if error['error out']['status']:
        raise LV_to_Py_Error


if __name__ == "__main__":
    main()
