# -*- coding: utf-8 -*-
from lta import Lta
import sys
from lta_err import Lta_Error
import time

#------------------- following code must be in all scripts--------------------
lta = Lta("127.0.0.1",60100)    # all scripts must create  an Lta object
try:
    lta.connect()                   # connect to the Labview Host
#---------------------Script code goes here------------------------------------
    UsrTimeout = lta.s.gettimeout()

    freq_list = [5000]    

    for freq in freq_list:    
        dlyTime = -2.0   # microseconds

        
        while (dlyTime < 2.0):
            print dlyTime

            ClkProperties=lta.__get__('Sync.ClockProperties')
            for element in ClkProperties[None]:
                if element['clClocks']['Name'] == "Digi_Trigger":
                    #element['clClocks']['Frequency'] = float(freq)   # Set Pgm_Pps Freuency
                    element['clClocks']['Delay'] = float(dlyTime)          #Set initial Pgm_Pps delay time
            lta.__set__('Sync.ClockProperties',ClkProperties)

            timeout = 5        
            while(timeout > 0): 
                time.sleep(10)
                locked = lta.__get__('Sync.LockStatus')
                print dlyTime
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

