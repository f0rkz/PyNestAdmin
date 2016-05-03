import os
import sys
# import ConfigParser
import argparse


# Project classes
from PyNestAdmin.NestPoller import NestPoller
from PyNestAdmin.NestConfig import NestConfig
from PyNestAdmin.NestDatabase import NestDatabase

CONFIG_FILE = os.path.join('server.cfg')

# Arguments are added here
argparser = argparse.ArgumentParser(description="PyNestAdmin: Python Nest administration tool")
argparser.add_argument('-i', '--initdb', help='Initialize/Reinstall the Database.'
                                              ' THIS WILL DELETE YOUR EXISTING HISTORY DATA', action='store_true')
argparser.add_argument('-w', '--web', help='Start the web server', action='store_true')
argparser.add_argument('-p', '--poll', help='Poll for new data', action='store_true')
argparser.add_argument('-c', '--configure', help='Generate a server.cfg file', action='store_true')
argparser.add_argument('-f', '--force', help='Force the operation without abandon.', action='store_true')
args = argparser.parse_args()

# Loads the configuration
if os.path.isfile(CONFIG_FILE):
    my_config = NestConfig(config=CONFIG_FILE)
    config = my_config.load_config()

# Catch if force is flagged. Else, force is false.
if args.force:
    force = True
else:
    force = False

if args.configure:
    my_config = NestConfig(config=CONFIG_FILE, force=force)
    configuration = my_config.configure()
    print configuration['message']

elif args.initdb:
    db = NestDatabase(config=config, force=force)
    init_db = db.init_db()
    print init_db['message']

elif args.poll:
    # The poller class here!
    this = NestPoller(config=config)
    this.doPoll()

elif args.web:
    pass

# No operations
else:
    sys.exit("No arguments given. Use --help for command usage.")