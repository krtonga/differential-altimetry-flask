import json
from app import app, db
from app.models import Sensor, Reading

db.create_all()

# PLACE STARTER DATA HERE:
# sensorFixed = json.loads("{\"sensor_id\":\"fixed 1\",\"fixed\":true, \"lat\":5.394125,\"lon\":-23.287345,\"alt\":841}")
# sensorRover = json.loads("{\"sensor_id\":\"rover 1\",\"fixed\":false}")
#
# Sensor.saveJson(sensorFixed)
# Sensor.saveJson(sensorRover)

db.session.commit()
