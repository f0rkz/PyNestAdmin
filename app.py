import os
import sys
import uuid
import json
import nest
import datetime

from flask import Flask, jsonify, request, abort, render_template, redirect, url_for, session, flash, Response
from flask_bootstrap import Bootstrap

# Forms
from flask_wtf import Form
from wtforms import StringField
from wtforms import PasswordField
from wtforms.validators import DataRequired

# Project classes
from PyNestAdmin.NestConfig import NestConfig
from PyNestAdmin.NestDatabase import NestDatabase


CONFIG_FILE = os.path.join('server.cfg')

if os.path.isfile(CONFIG_FILE):
    my_config = NestConfig(config=CONFIG_FILE)
    config = my_config.load_config()
else:
    sys.exit("No configuration found. Run PyNestAdmin.py --configure")

if config['nest_web']['ssl_crt'] and config['nest_web']['ssl_key']:
    ssl_enabled = True
else:
    ssl_enabled = False

app = Flask(__name__)
Bootstrap(app)

app.config['USERNAME'] = config['nest_web']['admin_user']
app.config['PASSWORD'] = config['nest_web']['admin_pass']
app.config['DATABASE'] = os.path.join('nest_data.db')
app.config['SECRET_KEY'] = uuid.uuid4().hex


# Forms
class OptionsForm(Form):
    nest_username = StringField('Nest Username', validators=[DataRequired()])
    nest_password = PasswordField('Nest Password', validators=[DataRequired()])
    admin_user = StringField('PyNestAdmin Username', validators=[DataRequired()])
    admin_pass = PasswordField('PyNestAdmin Password', validators=[DataRequired()])
    port = StringField('PyNestAdmin Port', validators=[DataRequired()])
    ip = StringField('PyNestAdmin Listen IP', validators=[DataRequired()])
    api_key = StringField('PyNestAdmin API Key', validators=[DataRequired()])

# Web facing routes
@app.route("/")
def root():
    if session.get('logged_in'):
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))


# Check for authentication
@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('root'))
    return render_template('pages/login.html', error=error)

# Options route
@app.route("/options", methods=['GET', 'POST'])
def options():
    pass

# API routes
api_base_uri = '/api/v1'


# Returns a json formatted dictionary of all of the data
@app.route('{}/data/all'.format(api_base_uri), methods=['GET'])
def all_data():
    key_received = request.args.get('key')
    api_key = config['nest_web']['api_key']
    if key_received == api_key:
        db = NestDatabase(config=config)
        data = db.get_data()
        return Response(json.dumps(data), mimetype='application/json')
    else:
        abort(401)


@app.route('{}/data/<serial>'.format(api_base_uri), methods=['GET'])
def serial_data(serial):
    key_received = request.args.get('key')
    api_key = config['nest_web']['api_key']
    if key_received == api_key:
        db = NestDatabase(config=config)
        return Response(json.dumps(db.get_data_by_serial(serial=serial)), mimetype='application/json')
    else:
        abort(401)


@app.route('{}/serials'.format(api_base_uri), methods=['GET'])
def get_serials():
    key_received = request.args.get('key')
    api_key = config['nest_web']['api_key']
    if key_received == api_key:
        napi = nest.Nest(config['nest']['username'], config['nest']['password'])
        data = []
        for device in napi.devices:
            data.append(device.serial)
        return Response(json.dumps(data), mimetype='application/json')
    else:
        abort(401)

# Local weather for structure serial
@app.route('{}/weather/<serial>'.format(api_base_uri), methods=['GET'])
def get_weather(serial):
    key_received = request.args.get('key')
    api_key = config['nest_web']['api_key']
    if key_received == api_key:
        result = {}
        with nest.Nest(config['nest']['username'], config['nest']['password']) as napi:
            for structure in napi.structures:
                if structure.serial == serial:
                    weather = {
                        'outside_temp': structure.weather.current.temperature,
                        'outside_humidity': structure.weather.current.humidity,
                        'wind_azimuth': structure.weather.current.wind.azimuth,
                        'wind_speed': structure.weather.current.wind.kph,
                        'wind_direction': structure.weather.current.wind.direction,
                        'condition': structure.weather.current.condition,
                    }
                    # Hourly forecast
                    forecast = {}
                    for f in structure.weather.hourly:
                        forecast[f.datetime.strftime('%Y-%m-%d %H:%M:%S')] = {
                            'time': f.datetime.strftime('%Y-%m-%d %H:%M:%S'),
                            'temperature': f.temperature,
                            'humidity': f.humidity,
                            'wind_direction': f.wind.direction,
                            'wind_azimuth': f.wind.azimuth,
                        }
                    result['weather'] = weather
                    result['hourly_forecast'] = forecast
                    result['error'] = False
        return jsonify(result)
    else:
        abort(401)

# Get weather data for all structures
@app.route('{}/weather/all'.format(api_base_uri), methods=['GET'])
def get_weather_all():
    key_received = request.args.get('key')
    api_key = config['nest_web']['api_key']
    if key_received == api_key:
        result = {}
        with nest.Nest(config['nest']['username'], config['nest']['password']) as napi:
            for structure in napi.structures:
                weather = {
                    'outside_temp': structure.weather.current.temperature,
                    'outside_humidity': structure.weather.current.humidity,
                    'wind_azimuth': structure.weather.current.wind.azimuth,
                    'wind_speed': structure.weather.current.wind.kph,
                    'wind_direction': structure.weather.current.wind.direction,
                    'condition': structure.weather.current.condition,
                    }
                # Hourly forecast
                forecast = {}
                for f in structure.weather.hourly:
                    forecast[f.datetime.strftime('%Y-%m-%d %H:%M:%S')] = {
                        'time': f.datetime.strftime('%Y-%m-%d %H:%M:%S'),
                        'temperature': f.temperature,
                        'humidity': f.humidity,
                        'wind_direction': f.wind.direction,
                        'wind_azimuth': f.wind.azimuth,
                    }
                result[structure.serial] = weather
                result[structure.serial]['forecast'] = forecast
                result['error'] = False
        return jsonify(result)
    else:
        abort(401)


@app.route('{}/set/<serial>/temperature/<temp>'.format(api_base_uri), methods=['GET'])
def set_temperature(serial, temp):
    key_received = request.args.get('key')
    api_key = config['nest_web']['api_key']
    if key_received == api_key:
        result = {}
        # napi = nest.Nest(config['nest']['username'], config['nest']['password'])
        with nest.Nest(config['nest']['username'], config['nest']['password']) as napi:
            if int(temp) <= 8 or int(temp) >= 33:
                result['error'] = True
                result['message'] = "Value out of range: {}".format(int(temp))
            else:
                result['error'] = False
                for device in napi.devices:
                    if device.serial == serial:
                        device.temperature = int(temp)
                        result['temperature'] = device.target

        return jsonify(result)
    else:
        abort(401)

# Set heat/cool mode
@app.route('{}/set/<serial>/mode/<mode>'.format(api_base_uri), methods=['GET'])
def set_mode(serial, mode):
    key_received = request.args.get('key')
    api_key = config['nest_web']['api_key']
    if key_received == api_key:
        modes = ['heat', 'cool', 'heat-cool']
        result = {}
        for valid_mode in modes:
            if valid_mode == mode:
                validated_mode = mode
                result['error'] = False
        if not valid_mode:
            result['error'] = True
            result['message'] = '{received} is not a valid mode. Please use: {modes}'.format(received=mode, modes=modes)
        if not result['error']:
            with nest.Nest(config['nest']['username'], config['nest']['password']) as napi:
                for device in napi.devices:
                    if device.serial == serial:
                        device.mode = validated_mode
                        result['mode'] = device.mode
        return jsonify(result)
    else:
        abort(401)


@app.route('{}/set/<serial>/fan/<power>'.format(api_base_uri), methods=['GET'])
def set_fan(serial, power):
    key_received = request.args.get('key')
    api_key = config['nest_web']['api_key']
    if key_received == api_key:
        result = {}
        with nest.Nest(config['nest']['username'], config['nest']['password']) as napi:
            if int(power) == 1:
                for device in napi.devices:
                    if device.serial == serial:
                        device.fan = True
                        result['fan'] = device.fan
            elif int(power) == 0:
                for device in napi.devices:
                    if device.serial == serial:
                        device.fan = False
                        result['fan'] = device.fan
            else:
                result['error'] = True
                result['message'] = "Option out of range: {}".format(power)

        return jsonify(result)
    else:
        abort(401)

# This runs the application!
if __name__ == "__main__":
    # SSL
    if ssl_enabled:
        context = (os.path.join('ssl', config['nest_web']['ssl_crt']),
                   os.path.join('ssl', config['nest_web']['ssl_key']))
        app.run(host='0.0.0.0', port=int(config['nest_web']['port']), ssl_context=context, threaded=True)
    else:
        app.run(port=int(config['nest_web']['port']), debug=True, host=config['nest_web']['ip'], threaded=True)

