from flask import Flask 
from config import Config

# __name__ is a python var for the current module
app = Flask(__name__)
app.config.from_object(Config)

# must come at end as workaround for circular inputs
from app import routes