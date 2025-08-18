#!/usr/bin/bash

# Not working for me with git bash
# python3 ./main/los_helper.py $@

#-------------------


# Instead of running this file (run.sh) also try copying the above command directly into the prompt.
# My git bash connects to the server and prints but the input doesn't make it through.
# Could be that /bin/bash is the wrong bash.
# There is also the issue of a new terminal closing immediately when the process ends,
# so it's better to run from an already open terminal that will stay open.

#"c:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.10_3.10.3056.0_x64__qbz5n2kfra8p0\python3.10.exe" Documents\los-helper\repo\main\los_helper.py nope
#"c:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.10_3.10.3056.0_x64__qbz5n2kfra8p0\python3.10.exe" main\los_helper.py nope
#"c:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.10_3.10.3056.0_x64__qbz5n2kfra8p0\python3.10.exe" Documents\los-helper\repo\main\los_helper.py 
#"c:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.10_3.10.3056.0_x64__qbz5n2kfra8p0\python3.10.exe" Documents\los-helper\repo\main\los_helper.py
# cd Documents\los-helper\repo
#"c:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.10_3.10.3056.0_x64__qbz5n2kfra8p0\python3.10.exe" "./main/los_helper.py" balancedbarb ma*****

# Powershell
#cd ../../Users/lauri/Documets/los-helper/repo
#. "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.10_3.10.3056.0_x64__qbz5n2kfra8p0\python3.10.exe" "./main/los_helper.py" balancedbarb ma*****

# Git bash
# cd /c/Users/lauri/Documents/los-helper/repo
#"/c/Program Files/WindowsApps/PythonSoftwareFoundation.Python.3.10_3.10.3056.0_x64__qbz5n2kfra8p0\python3.10.exe" "./main/los_helper.py" balancedbarb ma*****
# without the comment character #

# CMD
# cd Documents/los-helper/repo
#cd Documents/los-helper/hd_copy
#"C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.10_3.10.3056.0_x64__qbz5n2kfra8p0\python3.10.exe" "./main/los_helper.py" balancedbarb ma*****
# (cd main
#"C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.10_3.10.3056.0_x64__qbz5n2kfra8p0\python3.10.exe" "./los_helper.py" balancedbarb ma*****

#Go instead to hd_copy
#Make sure ./maplos.db looks good
# Ok got it working

#(Delete .lnk)
# python3.10.exe main/los_helper.py balancedbarb ****


cd Documents/los-helper/hd_copy
python3.10.exe main/los_helper.py balancedbarb mazemab



