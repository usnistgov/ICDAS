# -*- coding: utf-8 -*-
from lta import Lta
import sys
from lta_err import Lta_Error
#import numpy as np
import time

#------------------- following code must be in all scripts--------------------
lta = Lta("127.0.0.1",60100)    # all scripts must create  an Lta object
try:
    lta.connect()                   # connect to the Labview Host
#---------------------Script code goes here------------------------------------
    UsrTimeout = lta.s.gettimeout()
    count=20
    
    while (count > 0):
        timeout = 5
        while(timeout > 0): 
                time.sleep(1)
                locked = lta.__get__('Sync.LockStatus')
                print count
                if locked[None] == True:
                    lta.s.settimeout(1000)               
                    lta.__run__() 
                    lta.s.settimeout(UsrTimeout)
                    break
                timeout = timeout - 1
        count = count - 1

                
        if locked[None] != True:
            raise Exception ('Sync module is not locked')
                
   
#------------------all scripts should send their errors to labview------------
except Exception as ex:
    err = Lta_Error(ex,sys.exc_info())  #format a labview error
    lta.send_error(err,3,'Abort')       #send the error to labview for display
    lta.close()
    print err

    