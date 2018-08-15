from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import db
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User
from app.auth import auth_bp


@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('web.index'))
    form = LoginForm()
    if form.validate_on_submit(): #returns true on POST, if input is valid
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data) #for flask-login
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '': # must be relative url
            next_page = url_for('web.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('web.index'))


@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('web.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.append(user)
        db.session.commit()
        flash('Congrats! You have registered!')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)
