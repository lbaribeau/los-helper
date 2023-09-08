# check if the bot is process is running and restart it if it is not
#!/bin/bash
# Import environment variables ...
#. /etc/profile

# rename this to restart_bot.sh - then you can create a cron job to run it

if ! ps ax | grep "[l]os_helper.py";
then
   echo "not running";
   nohup python3 main/los_helper.py Username password -grind -headless &;
else
   echo "running";
fi