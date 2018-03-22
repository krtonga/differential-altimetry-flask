import os 

class Config(object):
	# for countering CSRF attacks
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'