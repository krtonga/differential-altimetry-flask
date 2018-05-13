import json
from flask import render_template, flash, redirect, url_for, request, jsonify
from app.api import api_bp
from app.models import Sensor, Reading



@api_bp.route('/sensors', methods=['GET','POST'])
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


@api_bp.route('/readings', methods=['GET','POST'])
def readings():

	if request.method == "POST":
		# read request
		jsonReq = json.loads(request.data)
		if len(jsonReq) > 0:
			# ensure that sensor exists for these readings (assume one sensor/post)
			sensor_id = jsonReq[0].get('sensor_id')
			reading_sensor = Sensor.get(sensor_id)
			if reading_sensor is None:
				reading_sensor = Sensor(sensor_id=sensor_id, fixed=False)
				reading_sensor.save()
			# create readings from json
			for jsonItem in jsonReq:
				Reading.saveJson(jsonItem)
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
					oneSensorsReadings = Reading.get_sensor(id.sensor_id, count)
					for r in oneSensorsReadings:
						filtered.append(r)
				return createReadingsResponse(filtered)

			# query contains sensor id & count
			else:
				# return count readings from sensor with given sensor_id
				filtered = Reading.get_sensor(sid, count)
				return createReadingsResponse(filtered)

		# check if query contains sensor id, and start and end times
		else:
			start = request.args.get('start_time', -1, type=int)
			end = request.args.get('end_time', -1, type=int)
			if (start != -1) and (end != -1):
				if sid != '':
					filtered = Reading.get_sensor_range(sid, start, end)
				else:
					filtered = Reading.get_range(start, end)
				return createReadingsResponse(filtered)


	# parameters are missing
	response = jsonify({'error': 'Only the following queries are supported: count, sensor_id & count, start_time & end_time, sensor_id & start_time & end_time'})
	response.status_code = 400  # Bad Request
	return response


def createReadingsResponse(readings):
	if not readings:
		response = jsonify({})
		response.status_code = 204  # No Content
		return response
	else:
		response = jsonify([r.jsonify() for r in readings])
		response.status_code = 200  # Ok
		return response
	pass
