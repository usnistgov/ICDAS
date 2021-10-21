# -*- coding: utf-8 -*-
from lta import Lta
import sys
from lta_err import Lta_Error
import time
import math

#------------------- following code must be in all scripts--------------------
lta = Lta("127.0.0.1",60100)    # all scripts must create  an Lta object
try:
    lta.connect()                   # connect to the Labview Host
#---------------------Script code goes here------------------------------------
    UsrTimeout = lta.s.gettimeout()

    # index offsets to function params
    amplitude = 0
    dcOffset = 1
    dutyCycle = 2
    frequency = 3
    phase = 4
    waveform = 5


    freq_list = [5000, 2000, 1000, 500, 200, 100, 50] 

    for freq in freq_list:    
        dlyTime = -.600    # microseconds
        
#        
        while (dlyTime < .325):
              
#            sleepTime = 5
#            while (sleepTime > 0):
#                print sleepTime            
#                time.sleep(1)
#                sleepTime = sleepTime-1
            

            
            print 'freq',freq,'delay:',dlyTime,'us'
            
            time.sleep(2.5) 

            
            fcnParams = lta.__get__('FGen.FunctionParams')  # get the array of signal parameters
    
            for param in fcnParams[None]:
                param[frequency] = float(freq)
                
            lta.__set__('FGen.FunctionParams',fcnParams)
            
            ClkProperties=lta.__get__('Sync.ClockProperties')
            for element in ClkProperties[None]:
                if element['clClocks']['Name'] == "Pgm_PPS":
                    element['clClocks']['Delay'] = float(dlyTime)          #Set initial Pgm_Pps delay time
            lta.__set__('Sync.ClockProperties',ClkProperties)

 
            timeout = 5        
            while(timeout > 0): 
                time.sleep(10)
                locked = lta.__get__('Sync.LockStatus')
                if locked[None] == True:
                    lta.s.settimeout(90)               
                    lta.__run__() 
                    lta.s.settimeout(UsrTimeout)
                    break
                timeout = timeout - 1
                
            if locked[None] != True:
                raise Exception ('Sync module is not locked')
                
            dlyTime = dlyTime + 0.05


#------------------all scripts should send their errors to labview------------
except Exception as ex:
    err = Lta_Error(ex,sys.exc_info())  #format a labview error
    lta.send_error(err,3,'Abort')       #send the error to labview for display
    lta.close()
    print err

