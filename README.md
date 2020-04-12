# los-helper

los-helper is a python script meant to automate certain aspects of mudding.

## Installation

* Python3+
* Peewee - pip install peewee
* NetworkX - pip install networkx

## Running the helper

* Create a new account on the mud then logout
* Open a prompt in the los-helper/main directory and run "py los-helper.py Username Password"

## Running on a server

* Starting the report host from the reporting_website directory:
`sudo python -m SimpleHTTPServer 80`

~`export FLASK_APP=server.py`~
~`python -m flask run`~
* Starting the bot in headless (reporting mode):
`nohup python3.5 los_helper.py user pass -grind -fast -headless &`
* Copy the reporting website files to the root folder `~/`
`cp ~/los-helper/reporting_website/* ~/`

^ then you can hit the server and see your character's stats and stuff :)

## Startup Parameters
* -grind: starts SmartGrind immediately after the map loads
* -fast: sets mana_to_wait and magic requirements to 0
* -headless: pushes data to the report.json file in /main

## Setting up a new vm
sudo apt-get git
sudo curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
sudo python3.5 get-pip.py

## Modifying the Database
DB Browser for SQLite workers well
You can open multiple windows on Mac OSX with this command `/Applications/DB\ Browser\ for\ SQLite.app/Contents/MacOS/DB\ Browser\ for\ SQLite &`