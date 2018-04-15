import unittest, os, json
from app import app, db
from app.models import Sensor

class ApiTestCase(unittest.TestCase):
    """This class represents the api tests"""

    def setUp(self):
        self.client = app.test_client()
        self.sensorFixed = "{\"sensor_id\":\"fixed 1\",\"fixed\":true, \"lat\":5.394125,\"lon\":-23.287345,\"alt\":841}"
        self.sensorRover = "{\"sensor_id\":\"rover 1\",\"fixed\":false}"
        self.reading = '''[{
            "sensor_id": "sensor1",
            "calibration": true,
            "time": 1521245271.408,
            "duration": 0.94,
            "lat": -7.918233,
            "lon": -33.412813,
            "lat_lon_sd": 15,
            "uncal_pressure": 103242,
            "uncal_pressure_sd": 38.5,
            "uncal_temperature": 290.23,
            "uncal_temperature_sd": 1.2,
            "sample_count": 100
        }]'''

        with app.app_context():
            db.create_all()

    def test_sensor_creation(self):
        res = self.client.post('/sensors', data = self.sensorFixed)
        self.assertEqual(res.status_code, 201)
        self.assertIn('fixed 1', str(res.data))
        self.assertFalse(Sensor.get("fixed 1") is None)

    def test_sensor_creation_requires(self):
        res = self.client.post('/sensors', data="{\"sensor_id\":\"fixed invalid 1\",\"fixed\":true}")
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/sensors', data="{\"sensor_id\":\"fixed invalid 2\",\"fixed\":true, \"lat\":5.394125,\"lon\":-23.287345}")
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/sensors', data="{\"sensor_id\":\"rover invalid 1\",\"fixed\":true}")
        self.assertEqual(res.status_code, 400)

    def test_sensor_get_all(self):
        self.client.post('/sensors', data = self.sensorFixed)
        self.client.post('/sensors', data = self.sensorRover)

        res = self.client.get('/sensors')
        self.assertEquals(res.status_code, 200)
        self.assertEquals(res.data, '[\n  {\n    "alt": 841.0, \n    "fixed": true, \n    "lat": 5.394125, \n    "lon": -23.287345, \n    "sensor_id": "fixed 1"\n  }, \n  {\n    "fixed": false, \n    "sensor_id": "rover 1"\n  }\n]\n')

    def test_reading_creation(self):
        res = self.client.post('/readings', data = self.reading)
        self.assertEquals(res.status_code, 201)

        self.assertFalse(Sensor.get("sensor1") is None)

    def test_reading_get_count_for_sensor_id(self):
        self.client.post('/readings', data = self.reading)

        res = self.client.get('/readings', query_string = {'sensor_id':'sensor1','count':1})
        self.assertEquals(res.status_code, 200)
        self.assertEquals(res.data, '[\n  {\n    "calibration": true, \n    "duration": 0.94, \n    "id": 1, \n    "lat": -7.918233, \n    "lat_lon_sd": 15.0, \n    "lon": -33.412813, \n    "sample_count": 100, \n    "sensor_id": "sensor1", \n    "time": "Sat, 17 Mar 2018 03:07:51 GMT", \n    "uncal_pressure": 103242.0, \n    "uncal_pressure_sd": 38.5, \n    "uncal_temprature": 290.23, \n    "uncal_temprature_sd": 1.2\n  }\n]\n')

    def test_reading_get_none(self):
        res = self.client.get('/readings', query_string = {'sensor_id':'sensor1','count':1})
        self.assertEquals(res.status_code, 204)



    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

if __name__ == "__main__":
    if __name__ == '__main__':
        unittest.main()
