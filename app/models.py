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



# class Reading():
# 	sensor_id
# 	calibration
# 	time
# 	duration
# 	lat
# 	lon
# 	lat_lon_sd
# 	uncal_pressure
# 	uncal_pressure_sd
# 	uncal_temperature_sd
# 	uncal_temperature_sd
# 	sample_count

class Sensor(db.Model):
	id = db.Column(db.String(64), primary_key=True)
	fixed = db.Column(db.Boolean())
	lat = db.Float()
	lon = db.Float()
	alt = db.Float()
	points = db.relationship('Point', backref='sensor', lazy='dynamic')

	def __repr__(self):
		return '<Sensor {}>'.format(self.id)


class Point(db.Model):
	id = db.Column(db.String(64), primary_key=True)
	sensor_id = db.Column(db.String(64), db.ForeignKey('sensor.id'))
	time = db.Column(db.DateTime)
	lon = db.Column(db.Float)
	lat_lon_sd = db.Column(db.Float)
	alt = db.Column(db.Float)
	alt_sd = db.Column(db.Float)

	def __repr__(self):
		return '<Point {}>'.format(self.id)



