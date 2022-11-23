# -*- coding: utf-8 -*-
#import time
from lta import Lta
import sys
from lta_err import Lta_Error
import module_class as M
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
    @staticmethod
    def getParamIdx():
        #useful indices# 
        Xm=0;Fin=1;Pin=2;Fh=3;Ph=4;Kh=5;Fa=6;Ka=7;Fx=8;Kx=9;Rf=10;KaS=11;KxS=12;KfS=13;KrS=14;
        return Xm,Fin,Pin,Fh,Ph,Kh,Fa,Ka,Fx,Kx,Rf,KaS,KxS,KfS,KrS
    
      #constructor
    def __init__(self,Duration,Config,Vnom,Inom,PMUclass,Fs):
        
        self.lta = Lta("127.0.0.1",60100)    # all scripts must create  an Lta object
        
        try:
            self.lta.connect()                   # connect to the Labview Host
            
        except Exception as ex:
            err = Lta_Error(ex,sys.exc_info())  #format a labview error
            self.lta.send_error(err,3,'Abort')       #send the error to labview for display
            self.lta.close()
            print (err)        
            
        
        try: 
            if PMUclass != "M" and PMUclass != "P":
                raise Exception('Error: Unrecognizable PMU class')

        #Would be good to limit these to safe values 
            self.Duration = float(Duration)
            self.Config = Config

 
            self.Vnom = Vnom
            self.Inom = Inom            
            self.PMUclass = PMUclass
            self.Fs = Fs
            
            self.ntries = 30
            self.secwait = 60
            self.ecode = {5605}  #set of error codes under which we need to try again
            
            self.fgen = None
            self.analysis = None


        except Exception as ex:
            raise ex   
  
 # Initialize framework to default values 
    def set_init(self):
        try:
            """ Sets initial default values to the framework"""
            print("Setting default params")
            
        
            #Analysis.Duration
            self.analysis.duration = {None: self.Duration}
            self.analysis.set_duration
            
            #Analysis.Config
            self.analysis.config = {None: self.Config}
            self.analysis.set_config()
            #Error=lta.__set__('Analysis.PmuAnalysis.,Config',{None: self.Config})
            
            #Setting Waveform Params
            self.fgen.get_params()
            #WfrmParams = lta.__get__('FGen.NiPxi6733.,FunctionParams')
            
            #useful indices
            Xm = 0; Fin = 1; Pin = 2; Fh = 3
            VA = 0; VB = 1; VC = 2; IA = 3; IB = 4; IC = 5;
            
            # default values
            self.fgen.params['element 0'][Xm][VA:VC+1] = float(self.Vnom)
            self.fgen.params['element 0'][Xm][IA:IC+1] = float(self.Inom)
            self.fgen.params['element 0'][Fin][:] = self.Config['F0']
            self.fgen.params['element 0'][Pin][VA] = self.fgen.params['element 0'][Pin][IA] = float(0.)
            self.fgen.params['element 0'][Pin][VB] = self.fgen.params['element 0'][Pin][IB] = float(-120.)
            self.fgen.params['element 0'][Pin][VC] = self.fgen.params['element 0'][Pin][IC] = float(120.)
            self.fgen.params['element 0'][Fh:][:] = float(0.) #all remaining parameters are null   
            self.fgen.set_params()
            
            # WfrmParams[None][Xm][VA:VC+1] = float(self.Vnom)
            # WfrmParams[None][Xm][IA:IC+1] = float(self.Inom)
            # WfrmParams[None][Fin][:] = self.Config['F0']
            # WfrmParams[None][Pin][VA] = WfrmParams[None][Pin][IA] = float(0.)
            # WfrmParams[None][Pin][VB] = WfrmParams[None][Pin][IB] = float(-120.)
            # WfrmParams[None][Pin][VC] = WfrmParams[None][Pin][IC] = float(120.)
            # WfrmParams[None][Fh:][:] = float(0.) #all remaining parameters are null
            # Error = lta.__set__('FGen.NiPxi6733.,FunctionParams',WfrmParams)

            print("Initial Values have been set")

        except Exception as ex:
            raise ex


# Frequency Range tests
    """
    Uses the module instances:
        FGen.NiPxi65733.PMU (SteadyState)
        Analysis.PmuAnalysis.PMU (SteadyState)
    
    """
    def FreqRange(self):
        print ("Performing Freequency Range Tests")
        
        self.fgen = M.NPModuleFGen(class_type='NiPxi6733',instance='PMU (SteadyState)',lta=self.lta)
        self.analysis = M.NPModuleAnalysis(class_type='PmuAnalysis',instance='PMU (SteadyState)',lta=self.lta)
        
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
                #WfrmParams = lta.__get__('FGen.NiPxi6733.,FunctionParams')
                    
            except Exception as ex:
                raise ex
                                
            while freq<fStop: 
                print('freq = ',freq)
                self.fgen.params['element 0'][Fin][:] = float(freq)
                #WfrmParams[None][Fin][:] = float(freq)
                self.fgen.set_params()
                try:
                    #Error = lta.__set__('FGen.NiPxi6733.,FunctionParams',WfrmParams)
                    self.lta.s.settimeout(200)   
                    Error = self.lta.__multirun__(self.ntries,self.secwait,self.ecode)
                    self.lta.s.settimeout(10)                       
                except Exception as ex:
                    print (Error)
                    raise type(ex)(str(freq)+ex) 
                    
                freq += incr
                             
        except Exception as ex:
            raise type(ex) ("Frequency Range Test Failure:"+ex.message)
 
# Magnitude Range Tests
    def MagRange(self):
        """
        Uses the module instances:
        FGen.NiPxi65733.PMU (SteadyState)
        Analysis.PmuAnalysis.PMU (SteadyState)
    
        """        
        print ("Performing Magnitude Range Tests") 
        
        self.fgen = M.NPModuleFGen(class_type='NiPxi6733',instance='PMU (SteadyState)',lta=self.lta)
        self.analysis = M.NPModuleAnalysis(class_type='PmuAnalysis',instance='PMU (SteadyState)',lta=self.lta)        
        
        Xm = 0;   # Magnitude index into WfrmParams
        incr = 0.1;
        iMag = 0.1  
        vMag = 0.1
        if self.PMUclass != 'M':
            vMag = 0.8
        try:   
            try:
                self.set_init()
                #WfrmParams = lta.__get__('FGen.NiPxi6733.,FunctionParams')
                A = self.fgen.params['element 0'][Xm].copy()
            
            except Exception as ex:
                raise ex
                
            while iMag < 2.1:
                #print ('iMag = ',iMag, 'VMag = ',vMag)   
                self.fgen.params['element 0'][Xm][0:3] = float(vMag)*A[0:3]
                self.fgen.params['element 0'][Xm][3:7] = float(iMag)*A[3:7]                
                #WfrmParams[None][Xm][0:3] = float(vMag)*A[0:3]
                #WfrmParams[None][Xm][3:7] = float(iMag)*A[3:7]
                print('Magnitudes: ',self.fgen.params['element 0'][Xm])
                iMag += incr
                if vMag < 1.2:
                    vMag += incr
                    
                try:
                    #Error = lta.__set__('FGen.NiPxi6733.,FunctionParams',WfrmParams)
                    self.fgen.set_params()
                    self.lta.s.settimeout(200)   
                    Error = self.lta.__multirun__(self.ntries,self.secwait,self.ecode)
                    self.lta.s.settimeout(10)                       
                except Exception as ex:
                    print (Error)
                    raise type(ex)(ex.message)                     
                 
        except Exception as ex:
            raise type(ex) ("Magnitude Range Test Failure:"+ex.message)
           
# Harmonic Interfereing Signals test
    def Harm(self):
        """
        Uses the module instances:
        FGen.NiPxi65733.PMU (SteadyState)
        Analysis.PmuAnalysis.PMU (SteadyState)
    
        """                
        print ("Performing Harmonic Intefering Signal Tests")
        
        self.fgen = M.NPModuleFGen(class_type='NiPxi6733',instance='PMU (SteadyState)',lta=self.lta)
        self.analysis = M.NPModuleAnalysis(class_type='PmuAnalysis',instance='PMU (SteadyState)',lta=self.lta)                

        range = 50      # number of harmonics to test
        fund = self.Config['F0'] 
        Fh = 3          # index of harmonic frequency into WfrmParams
        Ph = 4          # index of Harmonic Phase in WfrmParams
        Kh = 5          # index of Harmonic Index
        incr = 2
        hFreq = fund * incr;

        try:
            try:
                self.set_init();
                #WfrmParams = lta.__get__('FGen.NiPxi6733.,FunctionParams')
                self.fgen.params['element 0'][Ph][:] = [0, -120, 120, 0, -120, 120 ]
                self.fgen.params['element 0'][Kh][:] = float(0.1)

                # WfrmParams = lta.__get__('FGen.NiPxi6733.,FunctionParams')
                # WfrmParams[None][Ph][:] = [0, -120, 120, 0, -120, 120 ]
                # WfrmParams[None][Kh][:] = float(0.1)
                
            except Exception as ex:
                raise ex
                
            while hFreq<=fund*range:
                print('harmonic number =', incr, ' frequency = ',hFreq)
                self.fgen.params['element 0'][Fh][:] = float(hFreq)
                self.fgen.set_params()
                #WfrmParams[None][Fh][:] = float(hFreq)
                try:
                    #Error = lta.__set__('FGen.NiPxi6733.,FunctionParams',WfrmParams)
                    self.lta.s.settimeout(200)                       
                    Error = self.lta.__multirun__(self.ntries,self.secwait,self.ecode)
                    self.lta.s.settimeout(10)                            
                                                                           
                except Exception as ex:
                    print (Error)
                    raise type(ex)(str(hFreq)+ex.message) 
                    
                incr += 1;
                hFreq = incr*fund                                    
                
        except Exception as ex:
            raise type(ex) ("Harmonic Test Failure:"+ex.message)

 # Interharmonic Intefering Signals test
    def IHarm(self):
        """
        Uses the module instances:
        FGen.NiPxi65733.PMU (SteadyState)
        Analysis.PmuAnalysis.PMU (SteadyState)
    
        """           
        print("Performing Interharmonic Intefering Signals Tests")
        
        self.fgen = M.NPModuleFGen(class_type='NiPxi6733',instance='PMU (SteadyState)',lta=self.lta)
        self.analysis = M.NPModuleAnalysis(class_type='PmuAnalysis',instance='PMU (SteadyState)',lta=self.lta)                

        

        Fh = 3          # index of harmonic frequency into WfrmParams
        Ph = 4          # index of Harmonic Phase in WfrmParams
        Kh = 5          # index of Harmonic Index
        
        try:
            try:
                self.set_init();
                #WfrmParams = lta.__get__('FGen.NiPxi6733.,FunctionParams')
            except Exception as ex:
                raise ex
                
            self.fgen.params['element 0'][Ph][:] = [0, -120, 120, 0, -120, 120 ]
            self.fgen.params['element 0'][Kh][:] = float(0.1)
            # WfrmParams[None][Ph][:] = [0, -120, 120, 0, -120, 120 ]
            # WfrmParams[None][Kh][:] = float(0.1)
            iFreq = self.Config['F0']
            iFreqList = []
            incr = 0
            
            # create a list of frequencies IAW 60255-118-1 table 2            
            while iFreq > 10:
                iFreq = self.Config['F0'] - self.Fs/2 - (0.1 * 2**incr)
                if iFreq < 10:
                    iFreq = 10
                #print '# ',incr,'Interharmonic Frequency = ', iFreq
                iFreqList.append(iFreq)
                incr += 1
                
            iFreqList.reverse()
            incr = 0
            
            while iFreq < 2 * self.Config['F0']:
                iFreq = self.Config['F0'] + self.Fs/2 + (0.1 * 2**incr)
                if iFreq > 2 * self.Config['F0']:
                    iFreq = 2 * self.Config['F0']
                #print '# ',incr,'Interharmonic Frequency = ',iFreq                    
                iFreqList.append(iFreq)
                incr +=1
                
            #iterate over the list of iterharmonic frequencies
            for iFreq in iFreqList:
                print('Interharmonic Frequency = ', iFreq)
                self.fgen.params['element 0'][Fh][:] = float(iFreq)
                self.fgen.set_params()
                #WfrmParams[None][Fh][:] = float(iFreq)
                try:
                    #Error = self.lta.__set__('FGen.NiPxi6733.,FunctionParams',WfrmParams)
                    self.lta.s.settimeout(200)                       
                    Error = self.lta.__multirun__(self.ntries,self.secwait,self.ecode)
                    self.lta.s.settimeout(10)                            
                                                                           
                except Exception as ex:
                    print (Error)
                    raise type(ex)(str(iFreq)+ex.message) 
                                     
        except Exception as ex:
            raise type(ex) ("Interharmonic Test Failure:"+ex.message)
# Measurement bandwidth (modulation)    
    def MeasBand(self):
        """
        Uses the module instances:
        FGen.NiPxi65733.PMU (Modulation)
        Analysis.PmuAnalysis.PMU (Modulation)
    
        """              
        print("Performing Measurement Bandwidth (Modulation) Tests")
        
        self.fgen = M.NPModuleFGen(class_type='NiPxi6733',instance='PMU (Modulation)',lta=self.lta)
        self.analysis = M.NPModuleAnalysis(class_type='PmuAnalysis',instance='PMU (Modulation)',lta=self.lta)                
        
        
        # Range of modulation frequency
        if self.PMUclass == "M":
            Fmax = 5.
            if self.Fs/5 < 5:
                Fmax = self.Fs/5
        elif self.PMUclass == "P":
            Fmax = 2.
            if self.Fs/10 < 2:
                Fmax = self.Fs/10
        else:
            raise Exception("Measurement Bandwidth Test Error: Unsupported PMU class" % self.PMUclass)
 
        
        # get the parameter indices        
        _,_,_,_,_,_,Fa,Ka,Fx,Kx,_,_,_,_,_=self.getParamIdx()
        #VA,VB,VC,IA,IB,IC=self.getPhaseIdx()               
        
        
        try:
            self.set_init()
            #WfrmParams = lta.__get__('FGen.NiPxi6733.,FunctionParams')
        except Exception as ex:
            raise type(ex)("Measurement Bandwidth Test - unable to get Waveform Parameters . " +ex.message)
            
        # Amplitude Modulation
        self.fgen.params['element 0'][Kx][:] = float(0.1)
        self.fgen.params['element 0'][Kx][:] = float(0.1)
        # WfrmParams[None][Ka][:] = float(0)
        # WfrmParams[None][Ka][:] = float(0)
        fmod = range(1,int(Fmax*10),2)+[int(Fmax*10)]
        
        # loop through the range of frequencies  
        print("Running Amplitude Modulaton Tests")
        for f in fmod:
            print("Fmod = ", float(f)/10)
            self.fgen.params['element 0'][Fx][:] = float(f)/10
            #WfrmParams[None][Fx][:] = float(f)/10
            
            # set the waveform params  
            self.fgen.set_params()
            # try:
            #     Error = lta.__set__('FGen.NiPxi6733.,FunctionParams',WfrmParams)
            # except Exception as ex:
            #     print (Error)
            #     raise type(ex)("Measurement Bandwidth Test - unable to set Waveform Parameters . " +ex.message)
            
            # run one test
            try:
                self.lta.s.settimeout(200)                       
                Error = self.lta.__multirun__(self.ntries,self.secwait,self.ecode)
                self.lta.s.settimeout(10)                            
                                                                           
            except Exception as ex:
                print (Error)
                raise type(ex)("Kx="+str(self.fgen.params['element 0'][Kx][1]) 
                                    +", fmod="+ str(f)+"Hz, Fs="+str(self.Fs)+". "+ex.message+ex.message) 
                                    
                                    
        self.fgen.params['element 0'][Fx][:] = float(0)
        self.fgen.params['element 0'][Kx][:] = float(0)
        # WfrmParams[None][Fx][:] = float(0)
        # WfrmParams[None][Kx][:] = float(0)
        
        # Phase Modulation Tests
        print ("Running Phase Modulation Tests")
        self.fgen.params['element 0'][Ka][:] = float(0.1)
        #WfrmParams[None][Ka][:] = float(0.1)
        for f in fmod:
            print ("Fmod = ", float(f)/10)
            self.fgen.params['element 0'][Fa][:] = float(f)/10
            #WfrmParams[None][Fa][:] = float(f)/10
            self.fgen.set_params()
            
            # set the waveform params            
            # try:
            #     Error = self.lta.__set__('FGen.NiPxi6733.,FunctionParams',WfrmParams)
            # except Exception as ex:
            #     print(Error)
            #     raise type(ex)("Measurement Bandwidth Test - unable to set Waveform Parameters . " +ex.message)
            
            # run one test
            try:
                self.lta.s.settimeout(200)                       
                Error = self.lta.__multirun__(self.ntries,self.secwait,self.ecode)
                self.lta.s.settimeout(10)                            
                                                                           
            except Exception as ex:
                print (Error)
                raise type(ex)("Ka="+str(self.fgen.params['element 0'][Ka][1]) 
                                    +", fmod="+ str(f)+"Hz, Fs="+str(self.Fs)+". "+ex.message+ex.message) 
                                    
           
# Step Changes
    def Step(self):
        """
        Uses the module instances:
        FGen.NiPxi65733.PMU (Step)
        Analysis.PmuAnalysis.PMU (Step)
    
        """              
        
        print("Performing Step Change Tests")
        
        self.fgen = M.NPModuleFGen(class_type='NiPxi6733',instance='PMU (Step)',lta=self.lta)
        self.analysis = M.NPModuleAnalysis(class_type='PmuAnalysis',instance='PMU (Step)',lta=self.lta)                             
        
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
                #params = lta.__get__('FGen.NiPxi6733.,FunctionParams')
                self.fgen.params['element 0'][KaS][:] = float(magAmpl)
                self.fgen.set_params()
                #params[None][KaS][:] = float(magAmpl)
                #Error = lta.__set__('FGen.NiPxi6733,FunctionParams',params)
                
                self.fgen.get_arbs()
                #params = lta.__get__('FGen.NiPxi6733.,FunctionArbs')  
                
            except Exception as ex:
                raise type(ex) ("Step Change Test Failure:"+ex.message)
                
                
            while iteration > 0:
                #print('iterations remaining = ', iteration ', T0 = ',stepTime) 
                self.fgen.arbs['FunctionConfig']['T0'] = -float(stepTime)
                #params['FunctionConfig']['T0'] = -float(stepTime)
                self.fgen.set_arbs()
                try: 
                    #Error = lta.__set__('FGen.NiPxi6733.,FunctionArbs',params)
                    self.lta.s.settimeout(200)
                    Error = self.lta.__multirun__(self.ntries,self.secwait,self.ecode)
                    self.lta.s.settimeout(10)                       
                except Exception as ex:
                    print (Error)
                    raise type(ex)(str(iteration)+ex.message) 
                    
                stepTime += incr
                iteration += -1
                
        except Exception as ex:
            raise type(ex) ("Step Change Test Failure:"+ex.message)
                    
           

# ------------------ MAIN SCRIPT ---------------------------------------------
#------------------- following code must be in all scripts--------------------
#lta = Lta("127.0.0.1",60100)    # all scripts must create  an Lta object

#try:
#    lta.connect()                   # connect to the Labview Host
#---------------------Script code goes here------------------------------------


#UsrTimeout = lta.s.gettimeout()

Duration = 1    # Analysis.Duration

# Analysis.Config
Config = OrderedDict()      
Config['F0'] = np.uint32(50) 
Config['SettlingTime']= 0.0
Config['AnalysisCycles'] = float(6.0)
Config['SampleRate'] = float(48000)
Config['NumChannels']= np.uint32(6)   

   
Fs_ini = 50.  #doesnt matter this default value, to be changed later
#Fs_list = {60:[10,12,15,20,30,60],50:[10,25,50], 63:[10]} #63 inserted for testing
Fs_list = {50:{50}}
Vnom = 70.
Inom = 5.
PMUclass = "M"
Fs = 50.

#list of exceptions             
ex_list = []


# StdTests instance
t = StdTests(Duration,Config,Vnom,Inom,PMUclass,Fs)



#list of tests to be performed
func_list = [t.FreqRange,
             #t.MagRange, 
             #t.Harm,
             #t.IHarm
             #t.MeasBand, 
             #t.RampFreq, 
             #t.Step 
             #t.RepLatency
             ]     



#execution of tests for each Fs
try:
    UsrTimeout = t.lta.s.gettimeout()

    for my_func in func_list:
        for Fs in Fs_list[Config['F0']]:
            #t.SetFs(Fs); print((("\n\n ---- Test for Fs = " + str(Fs))
            try:
                t.lta.s.settimeout(10)   
                my_func()
                t.lta.s.settimeout(UsrTimeout)
            except Exception as ex:
                t.lta.close()
                print("Exception going to LV in the end:")
                print(ex)
                ex_list.append(ex)
                err = Lta_Error(ex,sys.exc_info())  #format a labview error
                t.lta.send_error(err,3,'log')       #send the error to labview for log
    
    t.lta.close()
    print ("FINAL ERROR LIST::")
    print (ex_list)
    for ex in ex_list:
        err = Lta_Error(ex,sys.exc_info())  #format a labview error
        t.lta.send_error(err,3,'log')       #send the error to labview for log

#------------------all scripts should send their errors to labview------------
except Exception as ex:
    err = t.Lta_Error(ex,sys.exc_info())  #format a labview error
    t.lta.send_error(err,3,'Abort')       #send the error to labview for display
    t.lta.close()
    print (err)
