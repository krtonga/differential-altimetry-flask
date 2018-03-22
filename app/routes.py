from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
	user = {'username': 'Team'}
	points = [
		{
			'location': {'lat':'1.2', 'lng':'-3.4', 'acc':'16'},
			'sensor': {'temp':'23.4', 'prs':'1267.4'},
			'elevation': 23.5
		},
		{
			'location': {'lat':'1.2', 'lng':'-3.4', 'acc':'16'},
			'sensor': {'temp':'23.4', 'prs':'1267.4'},
			'elevation': 3.5
		},
		{
			'location': {'lat':'1.2', 'lng':'-3.4', 'acc':'16'},
			'sensor': {'temp':'23.4', 'prs':'1267.4'},
			'elevation': -0.5
		}
	]
	return render_template('index.html', title='Home', user = user, points=points)

@app.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit(): #returns true on POST, if input is valid
		flash('Login requested for user {}, remember_me={}'.format(
			form.username.data, form.remember_me.data))
		return redirect(url_for('index'))
	return render_template('login.html', title='Sign In', form=form)
