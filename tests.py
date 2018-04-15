import unittest, json, sys
from datetime import datetime, timedelta
from source.api import app
from app import app, db
from app.models import User, Sensor, Point, add_points, add_point

class UserModelCase(unittest.TestCase):
    def test_password_hashing(self):
        u = User(username='admin')
        u.set_password('dog')
        self.assertFalse(u.check_password('god'))
        self.assertTrue(u.check_password('dog'))

class SensorAndPointModelCase(unittest.TestCase):
    s_id = 's1'

    def setup(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_add_points(self):
        # sensor should not exist
        sensor = Sensor.query.filter_by(sensor_id=self.s_id).first()
        self.assertTrue(sensor is None)

        # add points pre sensor
        add_points(self.create_points(0, 3, self.s_id))

        # sensor should be created
        sensor = Sensor.query.filter_by(sensor_id=self.s_id).first()
        self.assertTrue(sensor)
        self.assertTrue(sensor.sensor_id == 's1')

        # points should be linked to sensor
        points = sensor.points.all()
        self.assertTrue(len(points) == 3)

        # add points to existing sensor
        add_points(self.create_points(3, 4, self.s_id))

        # database should be updated
        points = sensor.points.all()
        self.assertTrue(len(points) == 4)

        # should be able to update point
        point = points[0]
        newAlt = point.alt + 4
        point.alt = newAlt
        add_point(point)
        points = sensor.points.all()
        self.assertTrue(len(points) == 4)
        self.assertTrue(newAlt == points[0].alt)


def create_points(self, min, max, sensorId):
    now = datetime.utcnow()
    points = []
    for x in range(min, max):
        points.append(Point(id='p'+str(x),
                            sensor_id=sensorId,
                            time=now, lat=(x*1.1),
                            lon=(x*-1.1),
                            lat_lon_sd=(x*12),
                            alt=(x*1.2),
                            alt_sd=(x*23)))
    return points

if __name__ == '__main__':
    unittest.main(verbosity=2)