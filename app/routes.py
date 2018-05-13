import json, datetime
from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask import render_template, flash, redirect, url_for, request, jsonify
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
		db.session.append(user)
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
		savedSensor = Sensor.saveJson(jsonReq)

		if savedSensor:
			response = jsonify(savedSensor.jsonify())
			response.status_code = 201 # Created
		else:
			response = jsonify({'error':'Sensor missing required fields. '
										'EXAMPLE JSON: 	sensorFixed = {\"sensor_id\":\"fixed1\",\"fixed\":true, \"lat\":5.394125,\"lon\":-23.287345,\"alt\":841}'
										'				sensorRover = {\"sensor_id\":\"rover1\",\"fixed\":false}'
								})
			response.status_code = 400 # Bad Request

	# GET
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
			# ensure that sensor exists for these readings (assume one sensor/post)
			sensor_id = jsonReq[0].get('sensor_id')
			readingSensor = Sensor.get(sensor_id)
			if readingSensor is None:
				readingSensor = Sensor(sensor_id=sensor_id, fixed=False)
				readingSensor.save()
			# create readings from json
			for jsonItem in jsonReq:
				reading = Reading(sensor_id=jsonItem.get('sensor_id'),
								  calibration=jsonItem.get('calibration'),
								  time=datetime.datetime.fromtimestamp(jsonItem.get('time')),
								  duration=jsonItem.get('duration'),
								  lat=jsonItem.get('lat'),
								  lon=jsonItem.get('lon'),
								  lat_lon_sd=jsonItem.get('lat_lon_sd'),
								  uncal_pressure=jsonItem.get('uncal_pressure'),
								  uncal_pressure_sd=jsonItem.get('uncal_pressure_sd'),
								  uncal_temperature=jsonItem.get('uncal_temperature'),
								  uncal_temperature_sd=jsonItem.get('uncal_temperature_sd'),
								  sample_count=jsonItem.get('sample_count'))
				reading.save()
		# generate server response
		response = jsonify(jsonReq)
		response.status_code = 201  # Created
		return response

	# GET
	else:
		sid = request.args.get('sensor_id', '', type=str)
		count = request.args.get('count', -1, type=int)

		# check if query contains count
		if count != -1:
			# query does not specify sensor id
			if sid == '':
				sensor_ids = Sensor.get_all_ids()
				filtered = []
				for id in sensor_ids:
					oneSensorsReadings = Reading.get(id.sensor_id, count)
					for r in oneSensorsReadings:
						filtered.append(r)
				response = jsonify([r.jsonify() for r in filtered])
				response.status_code = 200  # Ok
				return response

			# query contains sensor id & count
			else:
				# return count readings from sensor with given sensor_id
				filtered = Reading.get(sid, count)
				if not filtered:
					response = jsonify({})
					response.status_code = 204  # No Content
					return response
				else:
					response = jsonify([r.jsonify() for r in filtered])
					response.status_code = 200  # Ok
					return response
				pass

		# check if query contains sensor id, and start and end times
		# elif sid != '':
		# 	start = request.args.get('start_time', -1, type=int)
		# 	end = request.args.get('end_time', -1, type=int)
		# 	if (start != -1) and (end != -1):

		# else:


	# parameters are missing
	response = jsonify({'error': 'Only the following queries are supported: count, sensor_id & count, sensor_id & start_time & end_time'})
	response.status_code = 400  # Bad Request
	return response


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