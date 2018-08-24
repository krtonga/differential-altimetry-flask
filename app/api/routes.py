import json
import logging
import traceback
import sys
from sqlalchemy import exc
from flask import request, jsonify
from app.api import api_bp
from app.models import Sensor, Reading


@api_bp.route('/sensors', methods=['GET','POST'])
def sensors():
    logging.info('/sensors. method=%s. data=%s',request.method, request.data)
    if request.method == "POST":
        saved_sensor = Sensor.save_sensor_from_json(request)
        if saved_sensor:
            response = jsonify(Sensor.to_json(saved_sensor))
            # response = jsonify(Sensor.to_json(s) for s in saved_sensors)
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
        response = jsonify([Sensor.to_json(s) for s in sensors])
        response.status_code = 200 # Ok

    return response


@api_bp.route('/readings', methods=['GET','POST'])
def readings():
    # print('REQUEST: ', request, request.args, request.data)
    if request.method == "POST":
        result = Reading.save_readings_from_json(request)

        # generate server response
        response = jsonify(result)
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
                    one_sensors_readings = Reading.get_for_sensor(id.sensor_id, count)
                    for r in one_sensors_readings:
                        filtered.append(r)
                return create_readings_response(filtered)

            # query contains sensor id & count
            else:
                # return count readings from sensor with given sensor_id
                filtered = Reading.get_for_sensor(sid, count)
                return create_readings_response(filtered)

        # check if query contains sensor id, and start and end times
        else:
            start = request.args.get('start_time', -1, type=int)
            end = request.args.get('end_time', -1, type=int)
            if (start != -1) and (end != -1):
                if sid != '':
                    filtered = Reading.get_sensor_range(sid, start, end)
                else:
                    filtered = Reading.get_range(start, end)
                return create_readings_response(filtered)


    # parameters are missing
    response = jsonify({'error': 'Only the following queries are supported: count, sensor_id & count, start_time & end_time, sensor_id & start_time & end_time'})
    response.status_code = 400  # Bad Request
    return response


def create_readings_response(readings):
    if not readings:
        response = jsonify({})
        response.status_code = 204  # No Content
        return response
    else:
        response = jsonify([Reading.to_json(r) for r in readings])
        response.status_code = 200  # Ok
        return response
    pass
