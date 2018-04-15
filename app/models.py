from app import db
from app import login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
	return User.query.get(int(id))



class Reading(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	sensor_id = db.Column(db.String(64), db.ForeignKey('sensor.sensor_id'))
	calibration = db.Column(db.Boolean())
	time = db.Column(db.DateTime)
	duration = db.Column(db.Float())
	lat = db.Column(db.Float())
	lon = db.Column(db.Float())
	lat_lon_sd = db.Column(db.Float())
	uncal_pressure = db.Column(db.Float())
	uncal_pressure_sd = db.Column(db.Float())
	uncal_temperature = db.Column(db.Float())
	uncal_temperature_sd = db.Column(db.Float())
	sample_count = db.Column(db.Integer())

	def __repr__(self):
		return '<Reading {}>'.format(self.id)

	def save(self):
		db.session.add(self)
		db.session.commit()

	def jsonify(self):
		return {'id':self.id,
				'sensor_id':self.sensor_id,
				'calibration':self.calibration,
				'time':self.time,
				'duration':self.duration,
				'lat': self.lat,
				'lon':self.lon,
				'lat_lon_sd':self.lat_lon_sd,
				'uncal_pressure':self.uncal_pressure,
				'uncal_pressure_sd':self.uncal_pressure_sd,
				'uncal_temprature': self.uncal_temperature,
				'uncal_temprature_sd': self.uncal_temperature_sd,
				'sample_count':self.sample_count}


class Sensor(db.Model):
	sensor_id = db.Column(db.String(64), primary_key=True)
	fixed = db.Column(db.Boolean())
	lat = db.Column(db.Float())
	lon = db.Column(db.Float())
	alt = db.Column(db.Float())
	points = db.relationship('Point', backref='sensor', lazy='dynamic')
	readings = db.relationship('Reading', backref='sensor', lazy='dynamic')
	# TODO Add pressure_offset for fixed=false

	def __repr__(self):
		return '<Sensor {}>'.format(self.sensor_id)

	def save(self):
		db.session.add(self)
		db.session.commit()

	def jsonify(self):
		if self.fixed :
			return {'sensor_id':self.sensor_id,
					'fixed':self.fixed,
					'lat':self.lat,
					'lon':self.lon,
					'alt':self.alt}
		else :
			return {'sensor_id':self.sensor_id,
					'fixed':self.fixed}

	@staticmethod
	def get_all():
		return Sensor.query.all()

	@staticmethod
	def get(sensorId):
		return Sensor.query.filter_by(sensor_id=sensorId).first()


class Point(db.Model):
	id = db.Column(db.String(64), primary_key=True)
	sensor_id = db.Column(db.String(64), db.ForeignKey('sensor.sensor_id'))
	time = db.Column(db.DateTime)
	lat = db.Column(db.Float)
	lon = db.Column(db.Float)
	lat_lon_sd = db.Column(db.Float)
	alt = db.Column(db.Float)
	alt_sd = db.Column(db.Float)

	def __repr__(self):
		return '<Point {}>'.format(self.id)

def add_point(point):
	s_id = point.sensor_id
	sensor = Sensor.query.filter_by(sensor_id=s_id).first()
	if sensor is None:
		sensor = Sensor(sensor_id=s_id, fixed=False)
		sensor.points = [point]
		db.session.add(sensor)
	else:
		db.session.add(point)
	db.session.commit()

def add_points(points):
	s_id = points[0].sensor_id
	sensor = Sensor.query.filter_by(sensor_id=s_id).first()
	if sensor is None:
		sensor = Sensor(sensor_id=s_id, fixed=False)
		sensor.points = points
		db.session.add(sensor)
	else:
		db.session.add_all(points)
	db.session.commit()

