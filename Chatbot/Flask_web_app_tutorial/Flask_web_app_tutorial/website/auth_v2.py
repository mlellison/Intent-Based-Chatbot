from ast import ImportFrom
import re
from tabnanny import check
from turtle import xcor
from xmlrpc.client import boolean
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
import folium
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from .dates_checker_v1 import searchListing
import pandas as pd

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
            flash('Account created!', category= 'success')
            return redirect(url_for('views.home'))
    return render_template("sign-up.html")

@auth.route('/dates', methods=['GET','POST'])
def dates():
    if request.method =="POST":
        checkin = request.form.get("startdate")
        checkout = request.form.get("enddate")
        guests = int(request.form.get("guests"))
        if len(checkin) >=1:
            x=(checkin, checkout, guests)
            session["x"]= x
        else: 
            x=('2022-06-14', '2023-06-13', 2)
        return redirect(url_for("auth.this_map"))
    else:
        return render_template("vdates.html")

@auth.route('/listings')
def listings():
    if "x" in session:
        x= session["x"]
        x1= str(x[0])
        x2= str(x[1])
        x3 = int(x[2])
        b=searchListing(x1, x2, x3)
        data = pd.read_csv("website\static\data\listingHk.csv")
        data = data[data['id'].isin(b)]
        data = pd.DataFrame(data, columns = ['nameEn','latitude','longitude','host_name','price', 'id', 'review_scores_rating'])
        this_map = folium.Map(prefer_canvas=True)
        def plotDot(point):
            folium.CircleMarker(location=[point.latitude, point.longitude],
                        radius=10,
                        weight=2,#remove outline
                        tooltip= str(point.nameEn),
                        popup = 
                        "Host Name: " + str(point.host_name) + '<br>' +
                        "Price: " + str(point.price)+ '<br>' +
                        "Score: " + str(point.review_scores_rating),
                        parse_html=False,
                        fill_color='#000000').add_to(this_map)
        data.apply(plotDot, axis = 1)
        this_map.fit_bounds(this_map.get_bounds())
        folium_map = this_map
        return folium_map._repr_html_()
    else:
        return redirect(url_for("auth.dates"))

@auth.route('/this_map')
def map():
    from .maps import this_map
    folium_map = this_map
    return folium_map._repr_html_()

@auth.route('/map')
def this_map():
    return render_template("map.html")