import re
from turtle import xcor
from xmlrpc.client import boolean
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
import folium
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from .dates_checker_v1 import searchListing

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Try again', category='error')
        else:
            flash('User do not exist', category='error')
    return render_template("login.html",  boolean = True)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('.login'))

@auth.route('/sign-up', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = User.query.filter_by(email=email).first()

        if user:
            flash('User already exists', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 charaters', category='error')
        elif len(first_name) < 2:
            flash('Name must be greater than 1 charater', category='error')
        elif password1 != password2:
            flash('Passwords do not match', category='error')
        elif len(password1) < 7:
            flash('Password is too short needs to be 7 charaters', category='error')
        else:
            #add user to database
            new_user = User(email= email, first_name=first_name, password=generate_password_hash(password1,method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(user, remember=True)
            flash('Account created!', category= 'success')
            return redirect(url_for('views.home'))
    return render_template("sign-up.html")

@auth.route('/this_map')
def map():
    from .maps import this_map
    folium_map = this_map
    return folium_map._repr_html_()

@auth.route('/map')
def this_map():
    return render_template("map.html")

@auth.route('/dates', methods=['GET','POST'])
def dates():
    if request.method == 'POST':
        checkin = request.form.get('startdate')
        checkout = request.form.get('enddate')
        guests = int(request.form.get('guests'))
        if checkin > checkout:
            flash('Check in date must be less than check out date', category='error')
        elif len(checkin) == 0:
            flash('Required checkin date', category='error')
        elif len(checkout) == 0:
            flash('Required checkout date', category='error')
        elif guests == 0:
            flash('Required atleast 1 guest', category='error')
        else:
            flash('lets go explore!', category= 'success')
            return redirect(url_for('.this_map'))
    return render_template("vdates.html")

