# check if the bot is process is running and restart it if it is not
#!/bin/bash
# Import environment variables ...
#. /etc/profile

if ! ps ax | grep "[l]os_helper.py";
then
   echo "not running";
   nohup python3 main/los_helper.py Username password -grind -headless &;
else
   echo "running";
fi