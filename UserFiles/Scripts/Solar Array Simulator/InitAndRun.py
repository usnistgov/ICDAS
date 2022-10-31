"""
This script initates both the NHR9200 and the Chroma Load and configures them
so that the NHR9200 is operating as a current source charge mode with no
voltage limit and the Chroma is operating as a constant voltage load.

"""
# -----------------------  Labview Test Autppmation modules ------------------
from lta import Lta
from module_class import NPModuleAcPwr
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

    # Instantiate NPModuleAcPwr instances for the NHRDC and the Chroma Load
    nhr_dc = NPModuleAcPwr(class_type='NHRDCPower', instance="SolarArraySim", lta=lta )
    chroma_load = NPModuleAcPwr(class_type='ChromaAcLoad', instance='SolarArraySim', lta=lta)

    # when the Init and Run scripts complete, the nhr_dc will have voltage control enabled.
    nhr_dc.get_config()
    nhr_dc.config['NHRDC']['Modules'][0]['Device(s)Settings']['OutputSettings']['Enable Voltage'] = False
    nhr_dc.set_config()

    # get measurements from the Chroma Load
    chroma_load.get_config()
    print(chroma_load.config)
    # chroma_load.config['Device Properties']['Phases'][0]['Config']['Load Voltage (V/Vrms)'] = 10.0
    # chroma_load.set_config()
    # chroma_load.get_meas()
    # print(chroma_load.meas)

    # all done
    lta.close

if __name__ == "__main__":
    main()
