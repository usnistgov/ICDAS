[rngSync]
rngSync = "Dyn3 PMU Cal"

[rngFGen]
rngFGen = "PMU (Step)"

[rngDigitizer]
rngDigitizer = "PMU Cal (Finite)"

[rngSensor]
rngSensor = "C37.118 PMU"

[rngAnalysis]
rngAnalysis = "PMU (Step)"

[btnHideMods]
btnHideMods = "TRUE"

[Test Script]
Test Script = "PmuConformity\\MainScript.py"

[Test File]
Test File = "PmuConformity\\PMUCal (Step).tst"

[Test Configuration]
Test Configuration.<size(s)> = "5"
Test Configuration 0.Script Name = "Script"
Test Configuration 0.INI File Path = "UserFiles-PMU\\Plugins\\Sync\\PXI_MultiTrig\\Dyn3_PMUCal.ini"
Test Configuration 1.Script Name = "Script"
Test Configuration 1.INI File Path = "UserFiles-PMU\\Plugins\\Sensor\\C37.118 PMU\\C37.118_PMU .91.ini"
Test Configuration 2.Script Name = "Script"
Test Configuration 2.INI File Path = "UserFiles-PMU\\Plugins\\FGen\\NiPxi6733\\PMU (Step).ini"
Test Configuration 3.Script Name = "Script"
Test Configuration 3.INI File Path = "UserFiles-PMU\\Plugins\\Digitizer\\NiDaqMx\\PMU (SteadyState).ini"
Test Configuration 4.Script Name = "Script"
Test Configuration 4.INI File Path = "UserFiles-PMU\\Plugins\\Analysis\\PmuAnalysis\\PMU (Step).ini"