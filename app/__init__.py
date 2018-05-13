from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__) # __name__ is a python var for the current module
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

# import of bps must come after app and db are defined
from app.auth import auth_bp
app.register_blueprint(auth_bp)

from app.api import api_bp
app.register_blueprint(api_bp)

from app.web import web_bp
app.register_blueprint(web_bp)

# write logs to a file
# if not app.debug:
    # if not os.path.exists('logs'):
    #     os.mkdir('logs')
    # file_handler = RotatingFileHandler('logs/diffaltimetry.log', maxBytes=10240, backupCount=10)
    # file_handler.setFormatter(
    #     logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    # )
    # file_handler.setLevel(logging.ERROR)
    #
    # app.logger.addHandler(file_handler)
    # app.logger.setLevel(logging.ERROR)
    # app.logger.info('DiffAltimetry startup')

# must come at end as workaround for circular inputs
from app import models
from app.web import routes
