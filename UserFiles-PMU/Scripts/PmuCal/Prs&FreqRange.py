# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from lta import Lta
import sys
from lta_err import Lta_Error
import time

def pause():
    programPause = raw_input("Press the <ENTER> key to continue...")
#import math

#------------------- following code must be in all scripts--------------------
lta = Lta("127.0.0.1",60100)    # all scripts must create  an Lta object
try:
    lta.connect()                   # connect to the Labview Host
#---------------------Script code goes here------------------------------------
    UsrTimeout = lta.s.gettimeout()

    # index offsets to function params
    amplitude = 0
    frequency = 1
    phase = 2


    freq_list = [5000, 2000, 1000, 500, 200, 100, 80, 60, 50, 40] 

    for freq in freq_list:    
        print 'freq: ',freq,'Hz'
        time.sleep(2.5)
    
        fcnParams = lta.__get__('FGen.FunctionParams')
        fcnParams[None][frequency] = freq
        lta.__set__('FGen.FunctionParams',fcnParams)
        
        ClkProperties=lta.__get__('Sync.ClockProperties')
        for element in ClkProperties[None]:
 
             # set the PRS frequency:
             if element['clClocks']['Name'] == 'PRS':
                 element['clClocks']['Frequency'] = float(freq)

        lta.__set__('Sync.ClockProperties',ClkProperties)

        timeout = 5        
        while(timeout > 0): 
            time.sleep(10)
            locked = lta.__get__('Sync.LockStatus')
            if locked[None] == True:
                lta.s.settimeout(1000)               
                lta.__run__() 
                lta.s.settimeout(UsrTimeout)
                break
            timeout = timeout - 1
            
        if locked[None] != True:
            raise Exception ('Sync module is not locked')
    

#------------------all scripts should send their errors to labview------------
except Exception as ex:
    err = Lta_Error(ex,sys.exc_info())  #format a labview error
    lta.send_error(err,3,'Abort')       #send the error to labview for display
    lta.close()
    print err
