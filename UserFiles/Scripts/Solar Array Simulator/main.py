"""
Solar array Emulator (using NIST SG hardware main program

Author:  Allen Goldstein
email: allen.goldstein@ieee.org

requires NIST_SG_Solarsim which acn be installed into the pythin environment using:
'pip install git+https://github.com/usnistgov/NIST_SG_SolarSim'

:param: debug   debugging plots will be enabled (they aren't pretty but they work
:type: boolean

"""
debug = True    #if true, show the debug plots
vRef_Min = 25.0

# imports of custom modules
# SG_SolarSim
from sg_solarsim.ss_gui import SSTopGui
from sg_solarsim.mppt import MPPT

# LabVIEW test automation
from lta import Lta
from module_class import NPModuleAcPwr
import sys
from lta_err import Lta_Error
from ssm_commands import SsmScript
from ssm_commands import SsmAcPwrSetParameter

#imports of site packages
if debug:
    import matplotlib.pyplot as plt
import PySimpleGUI as sg

def main(debug=False):

    # simple popup to remind the user that the init_and_run scripts need to be run in ICDAS
    sg.popup('Make sure to run the init_and_run scripts in the ICDAS test manager before proceeding further')

    # connect to LabVIEW
    lta = Lta("127.0.0.1", 60100)  # all scripts must create  an Lta object
    try:
        lta.connect()  # connect to the Labview Host
    except Exception as ex:
        err = Lta_Error(ex, sys.exc_info())  # format a labview error
        lta.send_error(err, 3, 'Abort')  # send the error to labview for display
        lta.close()
        print(err)

    # Instantiate NPModuleAcPwr instances for the NHRDC and the Chroma Load
    nhr_dc = NPModuleAcPwr(class_type='NHRDCPower', instance="SolarArraySim", lta=lta )
    chroma_load = NPModuleAcPwr(class_type='ChromaAcLoad', instance='SolarArraySim', lta=lta)

    nhr_dc.get_config()
    #print(nhr_dc.config)
    # disable the NHRDC voltage control.  After this, the NHRDC will operate as a current source and go to any
    # voltage configured in the Chroma Load which is acting as a constant voltage load
    #nhr_dc.config['NHRDC']['Modules'][0]['Device(s)Settings']['OutputSettings']['Enable Voltage'] = False

    # instead of disabling the control, set the voltage to 45 volts
    nhr_dc.config['NHRDC']['Modules'][0]['Device(s)Settings']['OutputSettings']['Voltage (V)'] = float(45.0)
    nhr_dc.set_config()

    # get the load configuration to use in the outer loop
    chroma_load.get_config()

    # Instantiate the solarsim GUI
    ss_gui = SSTopGui(modlistname='CECMod', iv_plot=debug)
    ss_gui.start_gui()

    #instantiate the mppt tracker
    mppt = MPPT()
    v_ref = mppt.v_ref

    # if in debug mode, a crude plot of the mppt state
    if debug:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xbound(45)
        ax.set_ybound(10)
        fig.show()

    v_ref = vRef_Min
    v_ref_old = None
    while 1:
        if ss_gui.state == 'CLOSED':
            break

        # this is the program's "outer loop"

        # manage the gui
        ss_gui.run_gui()

        # if the TMY clock is running
        if ss_gui.clk != []:

            # determine the PV module parameters under the TMY clock's irradiance and temperature conditions
            IL, I0, Rs, Rsh, nNsVth = ss_gui.calcparams_desoto(g_eff=ss_gui.clk.g_eff, t_eff=ss_gui.clk.t_air)

            # get the measured voltage from the Chroma Load
            #time.sleep(1)
            chroma_load.get_meas()
            v_load = chroma_load.meas['element 0'][0]['BaseMeasurement']['Measurement Value']

            # find the PV module's model current given the load voltage
            pv_model_current = ss_gui.i_from_v(Rsh, Rs, nNsVth, v_load, I0, IL)
            if pv_model_current < 0:
                pv_model_current = 0

            # set the NHRDC current to the PV model current
            command = SsmAcPwrSetParameter(
                "NHRDCPower",
                "SolarArraySim",
                AcDc='DC',
                parameter='Current',
                value=str(pv_model_current)
            )
            script = SsmScript()
            command.prepend_to_script(script)
            lta.__send_script__(script)

            # the below uses set_config but the above uses the SSM SetParameter
            #nhr_dc.config['NHRDC']['Modules'][0]['Device(s)Settings']['OutputSettings']['Current (A)'] = float(pv_model_current)
            #nhr_dc.set_config()

            # get the voltage and current measurements from the NHRDC
            #time.sleep(1)
            nhr_dc.get_meas()
            #print(nhr_dc.meas)
            v_pv = nhr_dc.meas['element 0'][0][None][None]['Y'][0]
            i_pv = nhr_dc.meas['element 0'][1][None][None]['Y'][0]

            # iterate the MPPT to determine the next voltage setting for the load

            #this next bit of code overcomes limitations of the chroma load
            v_ref_new = mppt.inc_cond(v_pv, i_pv)
            if v_ref_old == None:
                v_ref_old = v_ref_new
            v_incr = v_ref_new - v_ref_old
            v_ref_old = v_ref_new
            v_ref += v_incr
            if v_ref <= vRef_Min:
                v_ref = vRef_Min
            print(f'v_pv= {v_pv}, i_pv={i_pv}, v_ref={v_ref}, v_incr={v_incr}')

            # set the chroma load to the new reference voltage
            command = SsmAcPwrSetParameter(
                "ChromaAcLoad",
                "SolarArraySim",
                AcDc='DC',
                parameter='Voltage',
                value=str(v_ref)
            )
            script = SsmScript()
            command.prepend_to_script(script)
            lta.__send_script__(script)
            # the below uses set_config but the above uses the SSM SetParameter
            #chroma_load.config['Device Properties']['Phases'][0]['Config']['Load Voltage (V/Vrms)'] = float(v_ref)
            #chroma_load.set_config()

            #--------------------------------------------------
            # loop ends here except for the MPPT plot for debugging
            if debug:
                ax.plot(v_pv, i_pv, marker = 'o')
                fig.show()

        else:
            v_ref = vRef_Min
            v_ref_old = None

            #ss_gui.fig.cla()

if __name__ == "__main__":
    main(debug=debug)
