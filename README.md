# PyNestAdmin: A python Nest Administration Tool

#Notes:
Web panel and graphs are currently in development. This should not be considered a "complete" tool yet.

If you want something faster, try my other tool written in php here:

https://github.com/f0rkz/Bootstrap-Nest-Administration-Tool

#Installation

## Prerequisites

In order to install PyNestAdmin, you need Python and pip installed.

In order to run this script the following needs to be installed:
###Windows
 - python2.7 or higher: https://www.python.org/downloads/
 - pip (should be included in the python installer)
 - Some sort of git integrated with cmd. [I use the program here](https://git-scm.com/download/win).

* Make sure python is configured in Windows PATH Environment

###Linux
 - python 2.7 or higher

`sudo apt-get install python`

 - pip

`sudo apt-get install python-pip`

Optional: virtualenv for your development environment.

## Step 1: Install the script and requirements

Clone the repository:

    git clone https://github.com/f0rkz/PyNestAdmin.git

Install the script requirements:

If using virtualenv:

    pip install -r requirements.txt

If not using virtualenv:

    sudo pip install -r requirements.txt

## Step 2: Configuration and Database Initialization

In order to utilize the script, you will need to configure it first:

    python PyNestAdmin.py --configure

Fill out the data prompted to you.

PyNestAdmin uses sqlite. Python supports this by default so no extra packages are required
to initialize your database. Run the following:

    python PyNestAdmin.py --initdb --force

Note the `--force` flag above. The `--initdb` flag will delete and recreate your database.
If you do not intend to delete the database, the `--force` flag can act like a safety.

## Step 3: Run your first poll

If you have properly configured PyNestAdmin, you are ready to poll for data:

    python PyNestAdmin.py --poll

## Step 4: Cron or scheduled task

It is recommended setting up a cron to run the `--poll` flag at regular intervals.
It is your choice how often to run the operation. I recommend every 5 minutes run the following:

    python PyNestAdmin.py --poll

Make sure you point to the proper script path in order to poll properly.

## Step 5: Run the webserver

PyNestAdmin is packaged with its own Flask framework webserver:

    python app.py

This will open up connections to the IP and port you specified in the configuration part of the install.

# API

PyNestAdmin is equipped with an api. Operations are checked with an API key defined in server.cfg.
It is recommended that you do not change your randomized key.

## API Endpoints

API connections need their key defined using variable: `key=yourApiKeyHere`

Example: `127.0.0.1:5000/api/v1/data/all?key=TheKeyGeneratedForMe`

### Informative Endpoints
    /api/v1/serials
Returns a list of serial numbers of devices assigned to your nest account

### Data Endpoints
    /api/v1/data/all
Returns data for all devices

    /api/v1/data/<serial_num>
Where <serial_num> is the serial of your nest.

### Weather Endpoint
    /api/v1/weather/all
Returns weather data for all of your assigned structures

    /api/v1/weather/<structure_serial>
Where <structure_serial> is your structure's serial number. Returns weather specific to the structure.

### Setter Endpoints
    /api/v1/set/<serial>/temperature/<temp>
Where serial is the serial number for the desired nest and temp is the desired temperature (in celcius!)

    /api/v1/set/<serial>/mode/<mode>
Where serial is the serial number for the desired nest and mode is one of the following:

    heat
    cool
    heat-cool

This will set the thermostat's operating mode.

    /api/v1/set/<serial>/fan/<power>
Where serial is the serial number for the desired nest and power is a binary digit (0 or 1).
Sets the fan status to on or off (or auto).