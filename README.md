# los-helper

los-helper is a python script meant to automate certain aspects of mudding.

## Installation

You need Python to run this - ideally < version 11

If you have Python version 11+ you'll need to create a separate environment for it using pyenv
* Install pyenv
    * PC via pip: https://github.com/pyenv-win/pyenv-win/blob/master/docs/installation.md#python-pip
    * Mac: brew install pyenv (you may need to install brew if you don't have it)
* Install Python 3.9.16
    * pyenv install 3.9.16
* If you have Python 3.9.16 install you can now use `source ./venv/bin/activate` skip the following required install steps below:
* When you're done you can close the terminal/command window or type `deactivate` to stop the pyenv instance

If you don't want to use venv and want to install onto your global python then:

* Python3+ + Pip
* sudo apt install python3-pip
* Peewee - pip install peewee
* NetworkX - pip install networkx

## Running the helper

* Copy the maplos-latest.db file => maplos.db so that the database can be found
* Create a new account on the mud then logout
* Open a prompt in the los-helper/main directory and run "python los-helper.py Username Password"

## Commands in the helper

* The bot is setup with a few useful commands:
    * find x: this will look for mobs and areas and return the corresponding Area IDs (sometimes this crashes the bot - bandits in particular for some reason)
        * eg. find Chapel
        * eg. find Cal
    * goto x: this will use the database to path towards an areaid - it'll open doors and stuff along the way
        * goto 2 (this is hardcoded as the Chapel in the database, ID 1 is the nearest unexplored node - careful with this as it can lead to death)
    * kk x: this will run a really basic physical attack rountine against a target mob
    * kkc x: this will run an attack routine that uses basic spells and abilities along with physical attacks
    * kk2 x: this is like kkc but will use your most powerful spells against a mob
        * eg. kk housewife
        * eg. kkc guard
        * eg. kk2 Gnardu
        * This will try to do smart targetting in the event a new mob enters
    * grind: this will start the bot in SmartGrind mode - using your class, spells, level etc to shop and fight mobs then go rest when appropriate
    * ** there are many other commands to document but I'm done for now :)

## Setup & Running Reporting server
* install node and npm
    * sudo apt install nodejs npm
* From the reporting_website folder
    * npm install
    * npm run serve
    * nohup npm run serve &
* Run the bot with -headless to write api files

### Old ways
* Starting the report host from the reporting_website directory:
python
`sudo python -m SimpleHTTPServer 80`
python3
`sudo python3 -m http.server 8080`
`nohup sudo python3 -m http.server 8080 &`

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
* `grep -a -B 200 "### Ferp was defeated"` (logs on death w/ 200 lines before, replace with your char name)

## Modifying the Database
* DBeaver is the best client - just open a new SQLite browser and go ham
* DB Browser for SQLite workers well
You can open multiple windows on Mac OSX with this command `/Applications/DB\ Browser\ for\ SQLite.app/Contents/MacOS/DB\ Browser\ for\ SQLite &`

## SQL to add new hidden path
insert into areaexit (area_from_id, area_to_id, exit_type_id, is_useable, is_hidden, note) values (2375, 2376, 115, 1, 1, 'empty cache room from locked armoury, key found on gnoll subchief')