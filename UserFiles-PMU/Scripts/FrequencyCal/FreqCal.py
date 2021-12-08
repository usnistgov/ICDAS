# -*- coding: utf-8 -*-
from lta import Lta
import sys
from lta_err import Lta_Error
from collections import OrderedDict
import numpy as np


class StdTests(object):
    """This object is intended to be a set of standard tests that shall follow the IEC Standard, 
    whose methods are capable of setting parameters and sending messages to actually run them through a 
    Labview framework
    
    Attributes:  
    
    Duration = Analysis Duration in seconds
    Config = Analysis Configuration
        Config[F0] = Nominal Frequency
        Config[SettlingTime] 
        Config[AnalysisCycles]
        Config[SampleRate] = Analysys Digitizer SampleRate
        Config[NumChannels]
    
    Fs = Instrument Reporting Rate 
    Vnom  = Nominal voltage level (defaults to RMS 70 VAC )
    Inom = Nominal current level (defaults to RMS 5 A )
    lta   - object to connect Labview host
    ntries - Number of running tries
    secwait - Seconds to wait before next try
    ecode - error code for trying again
    Dur - test duration (default 5 seconds)
    """
    
      #constructor
    #def __init__(self,Fs,F0,Fsamp,Vnom,Inom,Duration,PMUclass,lta,ntries,secwait,ecode):
    def __init__(self,Duration,Config,Vnom,Inom):
        try: 

        #Would be good to limit these to safe values 
            self.Duration = float(Duration)
            self.Config = Config

 
            self.Vnom = Vnom
            self.Inom = Inom                       
            self.ntries = 30
            self.secwait = 60
            self.ecode = {5605}  #set of error codes under which we need to try again

        except Exception as ex:
            raise ex   
 
    @staticmethod
    def getParamIdx():
        #useful indices# 
        Xm=0;Fin=1;Pin=2;Fh=3;Ph=4;Kh=5;Fa=6;Ka=7;Fx=8;Kx=9;Rf=10;KaS=11;KxS=12;KfS=13;KrS=14;
        return Xm,Fin,Pin,Fh,Ph,Kh,Fa,Ka,Fx,Kx,Rf,KaS,KxS,KfS,KrS
 

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

# Static verification of measuring and operating range
    def StaticRange(self):
        print ("Performing Static Range Tests")
        
        # Start ans stop frequencies dependi on PMU Class 
        range = 5
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

 # Measurement bandwidth (modulation)    
    def DynamicRange(self):
        print("Performing Dynamic Range tests")
        
        # fix frequency and vary index
            

        # Range of modulation frequency
        Fmax = 5.
        Kmax = 1
        Kincr = 0.1
        
        # get the parameter indices        
        _,_,_,_,_,_,Fa,Ka,_,_,_,_,_,_,_=self.getParamIdx()
        #VA,VB,VC,IA,IB,IC=self.getPhaseIdx()               
        
        
        try:
            self.set_init()
            WfrmParams = lta.__get__('FGen.FunctionParams')
        except Exception as ex:
            raise type(ex)("Measurement Bandwidth Test - unable to get Waveform Parameters . " +ex.message)
            
        # Frequency Modulation
        WfrmParams[None][Fa][:] = float(Fmax)
        kmod = range(1,int(Kmax*10),int(Kincr*10))+[int(Kmax*10)]
        
        # loop through the range of frequencies        
        for k in kmod:
            print "Kmod = ", float(k)/10
            WfrmParams[None][Ka][:] = float(k)/10
            
            # set the waveform params            
            try:
                Error = lta.__set__('FGen.FunctionParams',WfrmParams)
            except Exception as ex:
                print Error
                raise type(ex)("Measurement Bandwidth Test - unable to set Waveform Parameters . " +ex.message)
            
            # run one test
            try:
                lta.s.settimeout(200)                       
                Error = lta.__multirun__(self.ntries,self.secwait,self.ecode)
                lta.s.settimeout(10)                            
                                                                           
            except Exception as ex:
                print (Error)
                raise type(ex)("Kx="+str(WfrmParams[None][Fa][1]) 
                                    +", kmod="+ str(k)+", Fs="+str(self.Fs)+". "+ex.message+ex.message) 
                                    
                                    

# ------------------ MAIN SCRIPT ---------------------------------------------
#------------------- following code must be in all scripts--------------------
lta = Lta("127.0.0.1",60100)    # all scripts must create  an Lta object

try:
    lta.connect()                   # connect to the Labview Host
#---------------------Script code goes here------------------------------------

    print lta

    UsrTimeout = lta.s.gettimeout()
    
    Duration = 0.5    # Analysis.Duration
    
    # Analysis.Config
    Config = OrderedDict()      
    Config['F0'] = np.uint32(50) 
    Config['SettlingTime']= 0.0
    Config['AnalysisCycles'] = float(10.0)  # note, this will need to become ceil(F0/Fm) to capture at least 1 modulation cycle 
    Config['SampleRate'] = float(48000)
    Config['NumChannels']= np.uint32(6)   
    
   
    Fs_ini = 50.  #doesnt matter this default value, to be changed later
    #Fs_list = {60:[10,12,15,20,30,60],50:[10,25,50], 63:[10]} #63 inserted for testing
    Fs_list = {50:{50}}
    FSamp = 48000.
    Vnom = 70.
    Inom = 5.
    
    #list of exceptions             
    ex_list = []


    # StdTests instance
    t = StdTests(Duration,Config,Vnom,Inom)
    
    
    #list of tests to be performed
    func_list = [#t.StaticRange,
                 t.DynamicRange, 
                 #t.Harm, 
                 #t.RampFreq, 
                 #t.Step 
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

