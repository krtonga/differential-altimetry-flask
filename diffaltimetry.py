from app import app, db
from app.models import User, Sensor, Point
import logging
import traceback
import sys
from logging.handlers import RotatingFileHandler
from flask import jsonify
from  werkzeug.debug import get_current_traceback



@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Sensor': Sensor, 'Point': Point}

@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stdout.
        app.logger.addHandler(logging.StreamHandler(stream=sys.stdout))
        app.logger.setLevel(logging.INFO)

@app.errorhandler(500)
def internal_server_error(e):
    response = jsonify(e.message)
    response.status_code = 500 # Internal Server Error
    return response

if __name__ == '__main__':

    # handler = RotatingFileHandler('diff-alt-flask.log', maxBytes=10000, backupCount=1)
    # handler.setLevel(logging.INFO)
    # formatter = logging.Formatter("%(asctime)s | %(pathname)s:%(lineno)d | %(funcName)s | %(levelname)s | %(message)s ")
    # handler.setFormatter(formatter)
    # app.logger.addHandler(handler)
    # app.logger.setLevel(logging.DEBUG)
    # log = logging.getLogger('werkzeug')
    # log.setLevel(logging.DEBUG)
    # log.addHandler(handler)

    app.run(host='0.0.0.0')

    
