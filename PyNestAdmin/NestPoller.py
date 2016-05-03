import nest
import time
import calendar

from PyNestAdmin.Database import Database

class NestPoller(object):
    def __init__(self, config):
        self.config = config
        self.username = self.config['nest']['username']
        self.password = self.config['nest']['password']
        self.timestamp = calendar.timegm(time.gmtime())

    def doPoll(self):
        # Open a connection to the database
        db_obj = Database(config=self.config)
        db = db_obj.connect_db()
        c = db.cursor()
        # Create the nest api call
        napi = nest.Nest(self.username, self.password)

        data = {}

        # Loop through each device and gather data
        for device in napi.devices:
            data = {
                'time_stamp': self.timestamp,
                'structure_serial': device.structure.serial,
                'device_serial': device.serial,
                'heating': int(device.hvac_heater_state),
                'cooling': int(device.hvac_ac_state),
                'target_temp': 0 if isinstance(device.target, tuple) else device.target,
                'target_humidity': device.target_humidity,
                'current_temp': int(device.temperature),
                'humidity': device.humidity,
                'outside_temp': device.structure.weather.current.temperature,
                'outside_humidity': device.structure.weather.current.humidity,
                'outside_wind_speed': int(device.structure.weather.current.wind.kph),
                'outside_wind_dir': device.structure.weather.current.wind.direction,
                'away': int(device.structure.away),
                'mode': device.mode,
                'battery_level': device.battery_level,
            }

            sql = '''
            INSERT INTO data
            (
                time_stamp,
                structure_serial,
                device_serial,
                heating,
                cooling,
                target_temp,
                target_humidity,
                current_temp,
                outside_wind_speed,
                outside_wind_dir,
                humidity,
                outside_temp,
                outside_humidity,
                mode,
                away,
                battery_level
             )
             VALUES
             (
                :time_stamp,
                :structure_serial,
                :device_serial,
                :heating,
                :cooling,
                :target_temp,
                :target_humidity,
                :current_temp,
                :humidity,
                :outside_temp,
                :outside_humidity,
                :outside_wind_speed,
                :outside_wind_dir,
                :mode,
                :away,
                :battery_level
            )
            '''

            c.execute(sql, data)

            db.commit()

        # Tidy up the database connection
        db.close()

        return True
