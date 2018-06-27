import unittest, os, json
from app import app, db
from app.models import Sensor, Reading


class ApiTestCase(unittest.TestCase):
    """This class represents the api tests"""

    def setUp(self):
        self.client = app.test_client()
        self.sensorFixed = "{\"sensor_id\":\"fixed 1\",\"fixed\":true, \"lat\":5.394125,\"lon\":-23.287345,\"alt\":841}"
        self.sensorRover = "{\"sensor_id\":\"rover 1\",\"fixed\":false}"
        self.readings1 = '''[{
            "sensor_id": "sensor1",
            "calibration": true,
            "time": 1521245271.408,
            "height": 0.94,
            "lat": -7.918233,
            "lon": -33.412813,
            "lat_lon_sd": 15,
            "uncal_pressure": 103242,
            "uncal_pressure_sd": 38.5,
            "uncal_temperature": 290.23,
            "uncal_temperature_sd": 1.2,
            "sample_count": 100
        }, {
            "sensor_id": "sensor1",
            "calibration": false,
            "time": 1521245282.408,
            "height": 0.95,
            "lat": -7.918234,
            "lon": -33.412812,
            "lat_lon_sd": 16,
            "uncal_pressure": 103243,
            "uncal_pressure_sd": 38.6,
            "uncal_temperature": 290.24,
            "uncal_temperature_sd": 1.3,
            "sample_count": 100
        }]'''
        self.readings2 = '''[{
            "sensor_id": "sensor2",
            "calibration": true,
            "time": 1521245271.410,
            "height": 0.96,
            "lat": -7.918235,
            "lon": -33.412815,
            "lat_lon_sd": 17,
            "uncal_pressure": 103247,
            "uncal_pressure_sd": 38.7,
            "uncal_temperature": 290.27,
            "uncal_temperature_sd": 1.7,
            "sample_count": 100
        }, {
            "sensor_id": "sensor2",
            "calibration": false,
            "time": 1521245282.408,
            "height": 0.98,
            "lat": -7.918238,
            "lon": -33.412818,
            "lat_lon_sd": 18,
            "uncal_pressure": 103248,
            "uncal_pressure_sd": 38.8,
            "uncal_temperature": 290.28,
            "uncal_temperature_sd": 1.8,
            "sample_count": 100
        },  {
            "sensor_id": "sensor2",
            "calibration": false,
            "time": 1521245292.409,
            "height": 0.99,
            "lat": -7.918239,
            "lon": -33.412819,
            "lat_lon_sd": 19,
            "uncal_pressure": 103249,
            "uncal_pressure_sd": 38.9,
            "uncal_temperature": 290.29,
            "uncal_temperature_sd": 1.9,
            "sample_count": 100
        }]'''

        with app.app_context():
            db.create_all()


    def test_sensor_creation(self):
        res = self.client.post('/sensors', data=self.sensorFixed)
        self.assertEqual(res.status_code, 201)
        self.assertIn('fixed 1', str(res.data))
        self.assertFalse(Sensor.get("fixed 1") is None)

    def test_sensor_creation_requires(self):
        res = self.client.post('/sensors', data="{\"sensor_id\":\"fixed invalid 1\",\"fixed\":true}")
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/sensors',
                               data="{\"sensor_id\":\"fixed invalid 2\",\"fixed\":true, \"lat\":5.394125,\"lon\":-23.287345}")
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/sensors', data="{\"sensor_id\":\"rover invalid 1\",\"fixed\":true}")
        self.assertEqual(res.status_code, 400)

    def test_sensor_get_all(self):
        self.client.post('/sensors', data=self.sensorFixed)
        self.client.post('/sensors', data=self.sensorRover)

        res = self.client.get('/sensors')
        self.assertEquals(res.status_code, 200)
        self.assertEquals(res.data,
                          '[\n  {\n    "alt": 841.0, \n    "fixed": true, \n    "lat": 5.394125, \n    "lon": -23.287345, \n    "sensor_id": "fixed 1"\n  }, \n  {\n    "fixed": false, \n    "sensor_id": "rover 1"\n  }\n]\n')

    def test_sensor_get_ids(self):
        self.client.post('/sensors', data=self.sensorFixed)
        self.client.post('/sensors', data=self.sensorRover)

        res = Sensor.get_all_ids()
        self.assertTrue(len(res) is 2)
        # self.assertTrue('rover 1' in strRes)
        # self.assertTrue('fixed 1' in strRes)

    def test_reading_creation(self):
        res = self.client.post('/readings', data=self.readings1)
        res = self.client.post('/readings', data=self.readings2)
        self.assertEquals(res.status_code, 201)

        self.assertFalse(Sensor.get("sensor1") is None)
        self.assertFalse(Sensor.get("sensor2") is None)
        self.assertTrue(len(Reading.get_all()) is 5)

    def test_reading_get_count_for_sensor_id(self):
        self.client.post('/readings', data=self.readings1)
        self.client.post('/readings', data=self.readings2)

        res = self.client.get('/readings', query_string={'sensor_id': 'sensor1', 'count': 1})
        self.assertEquals(res.status_code, 200)
        self.assertEquals(res.data,
                          '[\n  {\n    "calibration": false, \n    "height": 0.95, \n    "lat": -7.918234, \n    "lat_lon_sd": 16.0, \n    "lon": -33.412812, \n    "sample_count": 100, \n    "sensor_id": "sensor1", \n    "time": "Sat, 17 Mar 2018 03:08:02 GMT", \n    "uncal_pressure": 103243.0, \n    "uncal_pressure_sd": 38.6, \n    "uncal_temprature": 290.24, \n    "uncal_temprature_sd": 1.3\n  }\n]\n')


    def test_should_not_enter_same_readings_twice(self):
        self.client.post('/readings', data=self.readings1)
        total = self.client.get('/readings', query_string={'sensor_id': 'sensor1', 'count': 100})
        self.assertEquals(len(json.loads(total.data)), 2)

        res = self.client.post('/readings', data=self.readings1)

        # returned response should be created successfully with empty array
        self.assertEquals(res.status_code, 201)
        self.assertEquals(len(json.loads(res.data)), 0)

        # only two items should be in the db
        total = self.client.get('/readings', query_string={'sensor_id': 'sensor1', 'count': 100})
        self.assertEquals(len(json.loads(total.data)), 2)

    def test_reading_post_should_handle_bytes(self):
        bytes = self.readings1.encode('utf-8')
        self.client.post('/readings', data=bytes)

        res = self.client.get('/readings', query_string={'sensor_id': 'sensor1', 'count': 1})
        self.assertEquals(res.status_code, 200)
        self.assertEquals(res.data,
                          '[\n  {\n    "calibration": false, \n    "height": 0.95, \n    "lat": -7.918234, \n    "lat_lon_sd": 16.0, \n    "lon": -33.412812, \n    "sample_count": 100, \n    "sensor_id": "sensor1", \n    "time": "Sat, 17 Mar 2018 03:08:02 GMT", \n    "uncal_pressure": 103243.0, \n    "uncal_pressure_sd": 38.6, \n    "uncal_temprature": 290.24, \n    "uncal_temprature_sd": 1.3\n  }\n]\n')

    def test_reading_get_count_for_all(self):
        self.client.post('/readings', data=self.readings1)
        self.client.post('/readings', data=self.readings2)

        res = self.client.get('/readings', query_string={'count': 2})

        self.assertEquals(res.status_code, 200)
        self.assertEquals(res.data,
                          '[\n  {\n    "calibration": false, \n    "height": 0.95, \n    "lat": -7.918234, \n    "lat_lon_sd": 16.0, \n    "lon": -33.412812, \n    "sample_count": 100, \n    "sensor_id": "sensor1", \n    "time": "Sat, 17 Mar 2018 03:08:02 GMT", \n    "uncal_pressure": 103243.0, \n    "uncal_pressure_sd": 38.6, \n    "uncal_temprature": 290.24, \n    "uncal_temprature_sd": 1.3\n  }, \n  {\n    "calibration": true, \n    "height": 0.94, \n    "lat": -7.918233, \n    "lat_lon_sd": 15.0, \n    "lon": -33.412813, \n    "sample_count": 100, \n    "sensor_id": "sensor1", \n    "time": "Sat, 17 Mar 2018 03:07:51 GMT", \n    "uncal_pressure": 103242.0, \n    "uncal_pressure_sd": 38.5, \n    "uncal_temprature": 290.23, \n    "uncal_temprature_sd": 1.2\n  }, \n  {\n    "calibration": false, \n    "height": 0.99, \n    "lat": -7.918239, \n    "lat_lon_sd": 19.0, \n    "lon": -33.412819, \n    "sample_count": 100, \n    "sensor_id": "sensor2", \n    "time": "Sat, 17 Mar 2018 03:08:12 GMT", \n    "uncal_pressure": 103249.0, \n    "uncal_pressure_sd": 38.9, \n    "uncal_temprature": 290.29, \n    "uncal_temprature_sd": 1.9\n  }, \n  {\n    "calibration": false, \n    "height": 0.98, \n    "lat": -7.918238, \n    "lat_lon_sd": 18.0, \n    "lon": -33.412818, \n    "sample_count": 100, \n    "sensor_id": "sensor2", \n    "time": "Sat, 17 Mar 2018 03:08:02 GMT", \n    "uncal_pressure": 103248.0, \n    "uncal_pressure_sd": 38.8, \n    "uncal_temprature": 290.28, \n    "uncal_temprature_sd": 1.8\n  }\n]\n')

    # NOTE EPOCH TIMES: 1521245271, 1521245282, 1521245271, 1521245282, 1521245292
    def test_reading_get_date_range_w_id(self):
        self.client.post('/readings', data=self.readings1)
        self.client.post('/readings', data=self.readings2)

        res = self.client.get('/readings', query_string={'sensor_id': 'sensor2',
                                                         'start_time':'1521245281',
                                                         'end_time':'1521245283'})
        self.assertEquals(res.data,
                         '[\n  {\n    "calibration": false, \n    "height": 0.98, \n    "lat": -7.918238, \n    "lat_lon_sd": 18.0, \n    "lon": -33.412818, \n    "sample_count": 100, \n    "sensor_id": "sensor2", \n    "time": "Sat, 17 Mar 2018 03:08:02 GMT", \n    "uncal_pressure": 103248.0, \n    "uncal_pressure_sd": 38.8, \n    "uncal_temprature": 290.28, \n    "uncal_temprature_sd": 1.8\n  }\n]\n')

    def test_reading_get_date_range(self):
        self.client.post('/readings', data=self.readings1)
        self.client.post('/readings', data=self.readings2)

        res = self.client.get('/readings', query_string={'start_time':'1521245281',
                                                         'end_time':'1521245283'})
        self.assertEquals(res.data,
                         '[\n  {\n    "calibration": false, \n    "height": 0.95, \n    "lat": -7.918234, \n    "lat_lon_sd": 16.0, \n    "lon": -33.412812, \n    "sample_count": 100, \n    "sensor_id": "sensor1", \n    "time": "Sat, 17 Mar 2018 03:08:02 GMT", \n    "uncal_pressure": 103243.0, \n    "uncal_pressure_sd": 38.6, \n    "uncal_temprature": 290.24, \n    "uncal_temprature_sd": 1.3\n  }, \n  {\n    "calibration": false, \n    "height": 0.98, \n    "lat": -7.918238, \n    "lat_lon_sd": 18.0, \n    "lon": -33.412818, \n    "sample_count": 100, \n    "sensor_id": "sensor2", \n    "time": "Sat, 17 Mar 2018 03:08:02 GMT", \n    "uncal_pressure": 103248.0, \n    "uncal_pressure_sd": 38.8, \n    "uncal_temprature": 290.28, \n    "uncal_temprature_sd": 1.8\n  }\n]\n')

    def test_reading_get_none(self):
        res = self.client.get('/readings', query_string={'sensor_id': 'sensor2', 'count': 1})
        self.assertEquals(res.status_code, 204)


    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    if __name__ == '__main__':
        unittest.main()
