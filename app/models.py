import json
import calendar
from datetime import datetime
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
    sensor_id = db.Column(db.String(64), db.ForeignKey('sensor.sensor_id'), primary_key=True)
    time = db.Column(db.DateTime, primary_key=True)
    calibration = db.Column(db.Boolean())
    height = db.Column(db.Float())
    lat = db.Column(db.Float())
    lon = db.Column(db.Float())
    lat_lon_sd = db.Column(db.Float())
    uncal_pressure = db.Column(db.Float())
    uncal_pressure_sd = db.Column(db.Float())
    uncal_temperature = db.Column(db.Float())
    uncal_temperature_sd = db.Column(db.Float())
    sample_count = db.Column(db.Integer())

    __table_args__ = (db.UniqueConstraint('sensor_id', 'time', name='sensor_time_uc'),)

    def __repr__(self):
        return '<Reading {}>'.format(self.sensor_id, self.time)

    def save(self):
        db.session.add(self)
        db.session.commit()

    # def to_csv(self):
    #     return [self.sensor_id,
    #             self.calibration, self.time, self.duration,
    #             self.lat, self.lon, self.lat_lon_sd,
    #             self.uncal_pressure, self.uncal_pressure_sd,
    #             self.uncal_temperature, self.uncal_temperature_sd,
    #             self.sample_count]

    # @staticmethod
    # def csv_headers(self):
    #     return ['sensor_id',
    #             'calibration', 'time', 'duration',
    #             'lat', 'lon', 'lat_lon_sd',
    #             'uncal_pressure', 'uncal_pressure_sd',
    #             'uncal_temperature', 'uncal_temperature_sd',
    #             'sample_count']

    def to_json(self):
        time = (self.time - datetime(1970, 1, 1)).total_seconds()  # converts to seconds since epoch
        # print(time)
        return {'sensor_id': self.sensor_id,
                'calibration': self.calibration,
                'time': time,
                'height': self.height,
                'lat': self.lat,
                'lon': self.lon,
                'lat_lon_sd': self.lat_lon_sd,
                'uncal_pressure': self.uncal_pressure,
                'uncal_pressure_sd': self.uncal_pressure_sd,
                'uncal_temperature': self.uncal_temperature,
                'uncal_temperature_sd': self.uncal_temperature_sd,
                'sample_count': self.sample_count}

    @staticmethod
    def from_json(json_reading):
        s_id = json_reading.get('sensor_id')
        time = json_reading.get('time')
        return Reading(sensor_id=s_id,
                       calibration=json_reading.get('calibration'),
                       time=datetime.utcfromtimestamp(time),
                       height=json_reading.get('height'),
                       lat=json_reading.get('lat'),
                       lon=json_reading.get('lon'),
                       lat_lon_sd=json_reading.get('lat_lon_sd'),
                       uncal_pressure=json_reading.get('uncal_pressure'),
                       uncal_pressure_sd=json_reading.get('uncal_pressure_sd'),
                       uncal_temperature=json_reading.get('uncal_temperature'),
                       uncal_temperature_sd=json_reading.get('uncal_temperature_sd'),
                       sample_count=json_reading.get('sample_count'))

    @staticmethod
    def save_readings_from_json(request):
        # read request
        str_req = request.data.decode('utf-8')
        json_req = json.loads(str_req)

        if len(json_req) > 0:
            result = Reading.save_readings(
                Reading.from_json(reading) for reading in json_req)
            return [Reading.to_json(r) for r in result]
        else:
            return []

    @staticmethod
    def save_readings(readings):
        readings_by_sensor = {}
        for reading in readings:
            readings_by_sensor.setdefault(reading.sensor_id, []).append(reading)
        result = []
        for sensor_id, readings in readings_by_sensor.items():
            if Sensor.query.filter_by(sensor_id=sensor_id).first():
                # TODO duplicates
                result = []
                for reading in readings:
                    saved = Reading.add_or_update_reading(reading)
                    if saved:
                        result.append(saved)
            else:
                db.session.add(Sensor(sensor_id=sensor_id, readings=readings))
                db.session.commit()
                result.extend(readings)
        return result

    @staticmethod
    def add_or_update_reading(reading):
        entry = Reading.get(reading)
        if entry is None:
            result = db.session.add(reading)
            db.session.commit()
            return reading
        else:
            entry.calibration = reading.calibration
            entry.height = reading.height
            entry.lat = reading.lat
            entry.lon = reading.lon
            entry.lat_lon_sd = reading.lat_lon_sd
            entry.uncal_pressure = reading.uncal_pressure
            entry.uncal_pressure_sd = reading.uncal_pressure_sd
            entry.uncal_temperature = reading.uncal_temperature
            entry.uncal_temperature_sd = reading.uncal_temperature_sd
            entry.sample_count = reading.sample_count
            db.session.commit()
            return None

    @staticmethod
    def get(reading):
        return Reading.query.filter_by(sensor_id=reading.sensor_id,
                                       time=reading.time).first()

    @staticmethod
    def get_all():
        return Reading.query.all()

    @staticmethod
    def get_for_sensor(sensor_id, count):
        return Reading.query.filter_by(sensor_id=sensor_id).order_by(Reading.time.desc()).limit(count).all()

    @staticmethod
    def get_range(start, end):
        return Reading.query.filter(Reading.time.between(datetime.utcfromtimestamp(start),
                                                         datetime.utcfromtimestamp(end)))

    @staticmethod
    def get_sensor_range(sensorId, start, end):
        return Reading.query.filter_by(sensor_id=sensorId).filter(
            Reading.time.between(datetime.utcfromtimestamp(start),
                                 datetime.utcfromtimestamp(end)))


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

    # def to_csv(self):
    #     return [self.sensor_id, self.fixed, self.lat, self.lon, self.alt]
    #
    # @staticmethod
    # def csv_headers(self):
    #     return ['sensor_id', 'fixed', 'latitude', 'longitude', 'elevation']

    def to_json(self):
        if self.fixed:
            return {'sensor_id': self.sensor_id,
                    'fixed': self.fixed,
                    'lat': self.lat,
                    'lon': self.lon,
                    'alt': self.alt}
        else:
            return {'sensor_id': self.sensor_id,
                    'fixed': self.fixed}

    @staticmethod
    def from_json(json_sensor):
        sensor_id = str(json_sensor.get('sensor_id', ''))
        fixed = json_sensor.get('fixed', False)
        lat = json_sensor.get('lat')
        lon = json_sensor.get('lon')
        alt = json_sensor.get('alt')

        # verify required fields
        if (sensor_id and fixed and lat and lon and alt) or (sensor_id and not fixed):
            return Sensor(sensor_id=sensor_id, fixed=fixed, lat=lat, lon=lon, alt=alt)

        # TODO throw exception

    @staticmethod
    def save_sensor_from_json(request):
        str_req = request.data.decode('utf-8')
        json_req = json.loads(str_req)
        sensor = Sensor.from_json(json_req)
        return Sensor.add_or_update_sensor(sensor)

    @staticmethod
    def add_or_update_sensor(sensor):
        if sensor is None:
            return None
        # TODO throw exception
        entry = Sensor.get(sensor.sensor_id)
        if entry is None:
            db.session.add(sensor)
        else:
            entry.fixed = sensor.fixed
            entry.lat = sensor.lat
            entry.lon = sensor.lon
            entry.alt = sensor.alt
        db.session.commit()
        return sensor

    @staticmethod
    def get(sensor_id):
        return Sensor.query.filter_by(sensor_id=sensor_id).first()

    @staticmethod
    def get_all_ids():
        return db.session.query(Sensor.sensor_id).distinct().all()

    @staticmethod
    def get_all():
        return Sensor.query.all()


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

# def add_point(point):
#     s_id = point.sensor_id
#     sensor = Sensor.query.filter_by(sensor_id=s_id).first()
#     if sensor is None:
#         sensor = Sensor(sensor_id=s_id, fixed=False)
#         sensor.points = [point]
#         db.session.add(sensor)
#     else:
#         db.session.add(point)
#     db.session.commit()
#
#
# def add_points(points):
#     s_id = points[0].sensor_id
#     sensor = Sensor.query.filter_by(sensor_id=s_id).first()
#     if sensor is None:
#         sensor = Sensor(sensor_id=s_id, fixed=False)
#         sensor.points = points
#         db.session.add(sensor)
#     else:
#         db.session.add_all(points)
#     db.session.commit()
