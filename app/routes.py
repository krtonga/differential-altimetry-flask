import json, datetime
from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.models import User, Sensor, Reading

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html', title='Home', sensors=Sensor.query.all())


@app.route('/login', methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit(): #returns true on POST, if input is valid
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data) #for flask-login
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '': # must be relative url
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))


@app.route('/register', methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congrats! You have registered!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)


@app.route('/sensor/<id>')
@login_required
def sensor(id):
	sensor = Sensor.query.filter_by(id=id).first_or_404()
	points = [
		{'lat':'-1', 'lon':'2.354', 'alt':'123'},
		{'lat':'-1', 'lon':'2.354', 'alt':'123'},
	]
	return render_template('sensor.html', sensor=sensor, points=points)


@app.route('/sensors', methods=['GET','POST'])
def sensors():
	if request.method == "POST":
		# read info from request
		jsonReq = json.loads(request.data)
		sensor_id = str(jsonReq.get('sensor_id',''))
		fixed = jsonReq.get('fixed', False)
		lat = jsonReq.get('lat')
		lon = jsonReq.get('lon')
		alt = jsonReq.get('alt')

		# verify required fields
		if (sensor_id and fixed and lat and lon and alt) or (sensor_id and not fixed):
			# create sensor, save & return
			sensor = Sensor(sensor_id=sensor_id, fixed=fixed, lat=lat, lon=lon, alt=alt)
			sensor.save()
			response = jsonify(sensor.jsonify())
			response.status_code = 201 # Created
		else:
			response = jsonify({'error':'Sensor missing required fields. '
										'EXAMPLE JSON: 	sensorFixed = {\"sensor_id\":\"fixed1\",\"fixed\":true, \"lat\":5.394125,\"lon\":-23.287345,\"alt\":841}'
										'				sensorRover = {\"sensor_id\":\"rover1\",\"fixed\":false}'
								})
			response.status_code = 400 # Bad Request

	else:
		sensors = Sensor.get_all()
		response = jsonify([s.jsonify() for s in sensors])
		response.status_code = 200 # Ok

	return response


@app.route('/readings', methods=['GET','POST'])
def readings():
	if request.method == "POST":
		# read request
		jsonReq = json.loads(request.data)
		if len(jsonReq) > 0:
			# ensure that sensor exists for these readings
			sensor_id = jsonReq[0].get('sensor_id')
			readingSensor = Sensor.get(sensor_id)
			if readingSensor is None:
				readingSensor = Sensor(sensor_id=sensor_id, fixed=False)
				readingSensor.save()
			# create readings from json
			for item in jsonReq:
				sensor_id = item.get('sensor_id')
				calibration = item.get('calibration')
				time = item.get('time')
				duration = item.get('duration')
				lat = item.get('lat')
				lon = item.get('lon')
				lat_lon_sd = item.get('lat_lon_sd')
				uncal_pressure = item.get('uncal_pressure')
				uncal_pressure_sd = item.get('uncal_pressure_sd')
				uncal_temperature = item.get('uncal_temperature')
				uncal_temperature_sd = item.get('uncal_temperature_sd')
				sample_count = item.get('sample_count')

				reading = Reading(sensor_id=sensor_id,
								  calibration=calibration,
								  time=datetime.datetime.fromtimestamp(time),
								  duration=duration,
								  lat=lat,
								  lon=lon,
								  lat_lon_sd=lat_lon_sd,
								  uncal_pressure = uncal_pressure,
								  uncal_pressure_sd = uncal_pressure_sd,
								  uncal_temperature = uncal_temperature,
								  uncal_temperature_sd = uncal_temperature_sd,
								  sample_count = sample_count)
				reading.save()
		# generate server response
		response = jsonify(jsonReq)
		response.status_code = 201  # Created

	else:
		sid = request.args.get('sensor_id', '', type=str)
		if sid != '':
			count = request.args.get('count', -1, type=int)
			if count != -1:
				sensor = Sensor.get(sid)
				if sensor is None:
					response = jsonify({})
					response.status_code = 204  # No Content
					return response
				else:
					filtered = sensor.readings.all()
					response = jsonify([r.jsonify() for r in filtered])
					response.status_code = 200  # Ok
					return response

			else:
				start = request.args.get('start_time', -1, type=int)
				end = request.args.get('end_time', -1, type=int)
				if (start == -1) or (end == -1):
					response = jsonify({'error': 'Only the following queries are supported: count, sensor_id & count, sensor_id & start_time & end_time'})
					response.status_code = 400  # Bad Request
					return response
				# else:
				# # TODO
			response = jsonify({'error': 'Only the following queries are supported: count, sensor_id & count, sensor_id & start_time & end_time'})
			response.status_code = 400  # Bad Request
		else:
			response = jsonify({'error': 'Only POST and GET allowed'})
			response.status_code = 405  # Method Not Allowed

	return response
	# elif request.method == "GET":
		# sensor_id
			# count
		# count
	# else:
	# 	response = jsonify({'error': 'Only POST and GET allowed'})
	# 	response.status_code = 405  # Method Not Allowed
	# return response


# @app.route('/points', methods=['GET', 'POST'])
# def points():
# 	# TODO remove post
# 	if request.method == "POST":
# 		# read info from request
# 		jsonReq = json.loads(request.data)
# 		id = str(jsonReq.get('id'))
# 		sensor_id = str(jsonReq.get('sensor_id'))
# 		time = jsonReq.get('time')
# 		lat = jsonReq.get('lat')
# 		lon = jsonReq.get('lon')
# 		lat_lon_sd = jsonReq.get('lat_lon_sd')
# 		alt = jsonReq.get('alt')
# 		alt_sd = jsonReq.get('alt_sd')
#
# 		point = Point(id=id, sensor_id=sensor_id, time=time, lat=lat, lon=lon, lat_lon_sd=lat_lon_sd, alt=alt, alt_sd=alt_sd)
# 		add_point(point)
#
# 	elif request.method == "GET":
# 		# sensor id
# 		# sid = request.args.get('sensor_id', -1, type=str)
# 		# if sid:
# 		# 	count = request.args.get('count', -1, type=int)
# 		# 	start = request.args.get('start_time', -1, type=int)
# 		# 	end = request.args.get('stop_time', -1, type=int)
# 		# else:
# 		# 	count = request.args.get('count', -1, type=int)
#
# 		points = Point.get_all()
# 		response = jsonify([s.jsonify() for s in sensors])
# 		response.status_code = 200  # Ok
# 	else:
# 		response = jsonify({'error': 'Only POST and GET allowed'})
# 		response.status_code = 405  # Method Not Allowed
# 	return response


# @app.route('/readings', methods=['GET','POST'])
# def readings():
# 	# post overwrites readings that have same id & time
#
# 	# get returns given count of readings for all sensors
# 	count = request.args.get('count', -1, type=int)
# 	posts = []
# 	sensors = Sensor.query.all()
# 	for sensor in sensors:


# @app.route('/readings?count=<count>')
# def readings(count):
# 	# returns given count of readings for all sensors
#
# @app.route('/readings?sensor_id=<id>&count=<count>')
# def readings(id, count):
# 	# returns given number of readings for given sensor
#
# @app.route('/points?count=<count>')
# def points(count):
# 	# returns given number of last points from each known roving sensor
#
# @app.route('/points?sensor_id=<id>&count=<count>')
# def points(id, count):
# 	# returns given number of last points for given sensor
#
# @app.route('/points?sensor_id=<id>&start_time<start_time>&stop_time=<stop_time>')
# def points(id, start_time, stop_time):
# 	# returns list in chronological order, may be paginated