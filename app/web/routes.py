from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required

from app.web import web_bp
from app.models import Sensor

import csv


@web_bp.route('/')
@web_bp.route('/index')
def index():
    return render_template('index.html', title='Home', sensors=Sensor.query.all())


@web_bp.route('/sensor/<id>')
@login_required
def sensor(id):
    sensor = Sensor.query.filter_by(id=id).first_or_404()
    points = [
        {'lat':'-1', 'lon':'2.354', 'alt':'123'},
        {'lat':'-1', 'lon':'2.354', 'alt':'123'},
    ]
    return render_template('sensor.html', sensor=sensor, points=points)