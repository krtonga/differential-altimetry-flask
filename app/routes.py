from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.models import User, Sensor, Point

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html', title='Home', sensors=Sensor.query.all())


@app.route('/login', methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit(): #returns true on POST, if input is valid
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data) #for flask-login
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '': # must be relative url
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))


@app.route('/register', methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congrats! You have registered!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)


@app.route('/sensor/<id>')
@login_required
def sensor(id):
	sensor = Sensor.query.filter_by(id=id).first_or_404()
	points = [
		{'lat':'-1', 'lon':'2.354', 'alt':'123'},
		{'lat':'-1', 'lon':'2.354', 'alt':'123'},
	]
	return render_template('sensor.html', sensor=sensor, points=points)