# -*- coding: utf-8 -*-
import time
from lta import Lta
import sys
from lta_err import Lta_Error
from collections import OrderedDict
import numpy as np

class StdTests(object):
    """This object is intended to be a set of standard tests that shall follow the test suit specification, 
    whose methods are capable of setting parameters and sending messages to actually run them through a 
    Labview framework
    
    Attributes:  
    
    Duration = Analysis Duration in seconds
    Config = Analysis Configuration
        Config[F0]
        Config[SettlingTime]
        Config[AnalysisCycles]
        Config[SampleRate] = Analysys Digitizer SampleRate
        Config[NumChannels]
    
    Fs = PMU Reporting Rate 
    Vnom  = Nominal voltage level (defaults to RMS 70 VAC )
    Inom = Nominal current level (defaults to RMS 5 A )
    PMUclass  = M or P class
    lta   - object to connect Labview host
    ntries - Number of running tries
    secwait - Seconds to wait before next try
    ecode - error code for trying again
    Dur - test duration (default 5 seconds)
    """
    
      #constructor
    #def __init__(self,Fs,F0,Fsamp,Vnom,Inom,Duration,PMUclass,lta,ntries,secwait,ecode):
    def __init__(self,Duration,Config,Vnom,Inom,PMUclass):
        try: 
            if PMUclass != "M" and PMUclass != "P":
                raise Exception('Error: Unrecognizable PMU class')

        #Would be good to limit these to safe values 
            self.Duration = float(Duration)
            self.Config = Config

 
            self.Vnom = Vnom
            self.Inom = Inom            
            self.PMUclass = PMUclass
            
            self.ntries = 30
            self.secwait = 60
            self.ecode = {5605}  #set of error codes under which we need to try again

        except Exception as ex:
            raise ex   
  
 # Initialize framework to default values 
    def set_init(self):
        try:
            """ Sets initial default values to the framework"""
            print("Setting default params")
            #Setting Duration
        
        
            #Analysis.Duration
            Error=lta.__set__('Analysis.Duration',{None: self.Duration})
            
            #Analysis.Config
            Error=lta.__set__('Analysis.Config',{None: self.Config})
            
            #Setting Waveform Params
            WfrmParams = lta.__get__('FGen.FunctionParams')
            
            #useful indices
            Xm = 0; Fin = 1; Pin = 2; Fh = 3
            VA = 0; VB = 1; VC = 2; IA = 3; IB = 4; IC = 5;
            
            # default values
            WfrmParams[None][Xm][VA:VC+1] = float(self.Vnom)
            WfrmParams[None][Xm][IA:IC+1] = float(self.Inom)
            WfrmParams[None][Fin][:] = self.Config['F0']
            WfrmParams[None][Pin][VA] = WfrmParams[None][Pin][IA] = float(0.)
            WfrmParams[None][Pin][VB] = WfrmParams[None][Pin][IB] = float(-120.)
            WfrmParams[None][Pin][VC] = WfrmParams[None][Pin][IC] = float(120.)
            WfrmParams[None][Fh:][:] = float(0.) #all remaining parameters are null
            Error = lta.__set__('FGen.FunctionParams',WfrmParams)

            print("Initial Values have been set")

        except Exception as ex:
            print Error
            raise ex


# Frequency Range tests
    def FreqRange(self):
        print ("Performing Freequency Range Tests")
        
        # Start ans stop frequencies dependi on PMU Class 
        range = 5
        if self.PMUclass != 'M':
            range = 2
            
        incr = 1  #frequency increment
        Fin = 1     # index to the frequency parameters
        
        freq = self.Config['F0'] - range
        fStop = freq + 2 * range + incr     # stop before ine step aftr the last
        
        try:          
            try:
                self.set_init()     # set up the initial parameters
                WfrmParams = lta.__get__('FGen.FunctionParams')
                    
            except Exception as ex:
                raise ex
                                
            while freq<fStop: 
                print 'freq = ',freq
                WfrmParams[None][Fin][:] = float(freq)
                try:
                    Error = lta.__set__('FGen.FunctionParams',WfrmParams)
                    lta.s.settimeout(200)   
                    Error = lta.__multirun__(self.ntries,self.secwait,self.ecode)
                    lta.s.settimeout(10)                       
                except Exception as ex:
                    print (Error)
                    raise type(ex)(str(freq)+ex.message) 
                    
                freq += incr
                             
        except Exception as ex:
            raise type(ex) ("Frequency Range Test Failure:"+ex.message)
            
            
# Step Changes
    def Step(self):
        print("Performing Step Chage Tests")
        
        stepTime = 1;
        incr = .1/self.Config['F0']
        iteration = 10 
        KaS = 12; KxS = 13  #index to step parameters
        magAmpl = 0.1
        angleAmpl = 10
        self.Duration = float(2)

        try:        
            try: 
                self.set_init()     # default function parameters
                
                # Step index                    
                params = lta.__get__('FGen.FunctionParams')
                params[None][KaS][:] = float(magAmpl)
                Error = lta.__set__('FGen.FunctionParams',params)
                
                params = lta.__get__('FGen.FunctionArbs')  
                
            except Exception as ex:
                raise type(ex) ("Step Change Test Failure:"+ex.message)
                
                
            while iteration > 0:
                print 'iterations remaining = ', iteration ', T0 = ',stepTime 
                params['FunctionConfig']['T0'] = -float(stepTime)
                try: 
                    Error = lta.__set__('FGen.FunctionArbs',params)
                    lta.s.settimeout(200)
                    Error = lta.__multirun__(self.ntries,self.secwait,self.ecode)
                    lta.s.settimeout(10)                       
                except Exception as ex:
                    print (Error)
                    raise type(ex)(str(iteration)+ex.message) 
                    
                stepTime += incr
                iteration += -1
                
        except Exception as ex:
            raise type(ex) ("Step Change Test Failure:"+ex.message)
                    
           

# ------------------ MAIN SCRIPT ---------------------------------------------
#------------------- following code must be in all scripts--------------------
lta = Lta("127.0.0.1",60100)    # all scripts must create  an Lta object

try:
    lta.connect()                   # connect to the Labview Host
#---------------------Script code goes here------------------------------------

    print lta

    UsrTimeout = lta.s.gettimeout()
    
    Duration = 1    # Analysis.Duration
    
    # Analysis.Config
    Config = OrderedDict()      
    Config['F0'] = np.uint32(50) 
    Config['SettlingTime']= 0.0
    Config['AnalysisCycles'] = float(6.0)
    Config['SampleRate'] = float(24000)
    Config['NumChannels']= np.uint32(6)   
    
   
    Fs_ini = 60.  #doesnt matter this default value, to be changed later
    #Fs_list = {60:[10,12,15,20,30,60],50:[10,25,50], 63:[10]} #63 inserted for testing
    Fs_list = {50:{50}}
    FSamp = 9600.
    Vnom = 70.
    Inom = 5.
    PMUclass = "M"
    
    #list of exceptions             
    ex_list = []


    # StdTests instance
    t = StdTests(Duration,Config,Vnom,Inom,PMUclass)
    
    
    
    #list of tests to be performed
    func_list = [#t.FreqRange,
                 #t.Magnitude, 
                 #t.Harm, 
                 #t.MeasBand, 
                 #t.RampFreq, 
                 t.Step 
                 #t.RepLatency
                 ]     



    #execution of tests for each Fs
    for my_func in func_list:
        for Fs in Fs_list[Config['F0']]:
            #t.SetFs(Fs); print("\n\n ---- Test for Fs = " + str(Fs))
            try:
                lta.s.settimeout(10)   
                my_func()
                lta.s.settimeout(UsrTimeout)
            except Exception as ex:
                print "Exception going to LV in the end:"
                print ex
                ex_list.append(ex)
                err = Lta_Error(ex,sys.exc_info())  #format a labview error
                lta.send_error(err,3,'log')       #send the error to labview for log
    
    print "FINAL ERROR LIST::"
    print ex_list
    for ex in ex_list:
        err = Lta_Error(ex,sys.exc_info())  #format a labview error
        lta.send_error(err,3,'log')       #send the error to labview for log

#------------------all scripts should send their errors to labview------------
except Exception as ex:
    err = Lta_Error(ex,sys.exc_info())  #format a labview error
    lta.send_error(err,3,'Abort')       #send the error to labview for display
    lta.close()
    print err
