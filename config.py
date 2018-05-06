import os 
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	# for countering CSRF attacks
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

	SQLALCHEMY_DATABASE_URI = \
		'sqlite:///' + os.path.join(basedir, 'diffaltimetry.db')
		# os.environ.get('DATABASE_URL') or \
	SQLALCHEMY_TRACK_MODIFICATIONS = False