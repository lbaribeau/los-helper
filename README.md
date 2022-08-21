# los-helper

los-helper is a python script meant to automate certain aspects of mudding.

## Installation

* Python3+ + Pip
* sudo apt install python3-pip
* Peewee - pip install peewee
* NetworkX - pip install networkx

## Reporting server
* sudo apt install nodejs npm
* From the reporting_website folder
    * npm install
    * npm run serve
* Run the bot with -headless to write api files

## Running the helper

* Create a new account on the mud then logout
* Open a prompt in the los-helper/main directory and run "py los-helper.py Username Password"

## Running on a server

* Deprecated
* Starting the report host from the reporting_website directory:
python
`sudo python -m SimpleHTTPServer 80`
python3
`sudo python3 -m http.server 8080`

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
* -headless: pushes data to the report.json file in /reporting_website/api
* -campslave: sits in the chapel then buffs and heals anyone who rests (w/ cooldowns)

## Running headlessly
This will run the bot headlessly so you can watch on the remote server - output goes to the nohup.out file so you can cat/grep as needed for debug info
`nohup python3 main/los-helper username password -grind -headless &`

This will run the bot headlessly so you can watch on the remote server - output goes to the nohup.out file so you can cat/grep as needed for debug info
`nohup sudo python3 -m http.server 8080 &`

## Setting up a new vm
sudo apt-get git
sudo curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
sudo python3.5 get-pip.py

## Helpful vm commands
* `pkill -f los` (kill all processes with los in the name)
* `grep -a -B 200 "### Ferp was defated"` (logs on death w/ 200 lines before, replace with your char name)

## Modifying the Database
* DBeaver is the best client - just open a new SQLite browser and go ham
* DB Browser for SQLite workers well
You can open multiple windows on Mac OSX with this command `/Applications/DB\ Browser\ for\ SQLite.app/Contents/MacOS/DB\ Browser\ for\ SQLite &`

## SQL to add new hidden path
insert into areaexit (area_from_id, area_to_id, exit_type_id, is_useable, is_hidden, note) values (2375, 2376, 115, 1, 1, 'empty cache room from locked armoury, key found on gnoll subchief')