import ConfigParser
import os
import uuid

class NestConfig(object):
    def __init__(self, config, force=False):
        self.config = config
        self.force = force

    def configure(self):
        result = {}
        parser = ConfigParser.RawConfigParser()
        # Exit the class with an error if a configuration is found
        if os.path.isfile(self.config) and not self.force:
            result['error'] = True
            result['message'] = "A configuration file has been found. Use --force to overwrite the current " \
                                "configuration."
            return result
        # No configuration file was found, do the configuration
        else:
            # Dev
            # Disabled options
            # {'section': 'nest', 'option': 'zipcode', 'info': 'Your Zipcode: ', 'required': True},
            nest_options = [
                {'section': 'nest', 'option': 'username', 'info': 'Your Nest.com Username: ', 'required': True},
                {'section': 'nest', 'option': 'password', 'info': 'Your Nest.com Password: ', 'required': True},
                {'section': 'nest_web', 'option': 'admin_user', 'info': 'Web Admin Username: ', 'required': True},
                {'section': 'nest_web', 'option': 'admin_pass', 'info': 'Web Admin Pass: ', 'required': True},
                {'section': 'nest_web', 'option': 'ssl_crt', 'info': 'SSL Certificate File (optional): ', 'required': False},
                {'section': 'nest_web', 'option': 'ssl_key', 'info': 'SSL Key File (optional): ', 'required': False},
                {'section': 'nest_web', 'option': 'port', 'info': 'Listen Port: ', 'required': True},
                {'section': 'nest_web', 'option': 'ip', 'info': 'Listen IP: ', 'required': True},
            ]
            # Add configuration sections here
            parser.add_section('nest')
            parser.add_section('nest_web')

            # Generate an API Key
            api_key = uuid.uuid4().hex

            # Loop through the nest_options listed dictionary and process each one.
            for option in nest_options:
                while True:
                    # Get input from the user
                    user_input = raw_input(option['info'])
                    # User gave input, initilize it in configparser
                    if user_input or option['required'] is False:
                        parser.set(option['section'], option['option'], user_input)
                        break

            # Set the API key
            parser.set('nest_web', 'api_key', api_key)

            # Save the configuration
            with open(self.config, 'wb') as configfile:
                parser.write(configfile)
            result['error'] = False
            result['message'] = '{} saved.'.format(self.config)

            return result

# Get this shit out of here. Its stupid and broken.
    def load_config(self):
        result = {}
        parser = ConfigParser.RawConfigParser()
        if os.path.isfile(self.config):
            parser.read(self.config)
            my_config = parser._sections
            result = my_config
            result['error'] = False
        else:
            result['error'] = True
            result['message'] = 'No configuration file present. Run --configure'
        return result