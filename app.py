from flask import Flask, render_template, redirect, session, g, request, jsonify, json, flash
from flask_debugtoolbar import DebugToolbarExtension
import requests
from werkzeug.exceptions import Unauthorized
from sqlalchemy.exc import IntegrityError
import os
from forms import UserAddForm, LoginForm, ProfileEditForm
from models import connect_db, db, User, Location

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///weatherly'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "carter")
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
API_key = '384549281a1b886956dff00758e198a3'

toolbar = DebugToolbarExtension(app)

connect_db(app)

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""
    session["user_zip"] = user.zip_code
    session[CURR_USER_KEY] = user.id
    session["username"] = user.username


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    if "user_zip" in session:
        del session["user_zip"]

def do_update(user):
    session["username"] = user.username
    session["user_zip"] = user.zip_code


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
                zip_code=form.location.data or None
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    flash('Logout success!')
    return redirect('/')


@app.route('/')
def home():
    top_locs = Location.query.order_by(Location.times_searched.desc()).limit(10).all()
    if session.get("user_zip"):
        user_zip = session.get("user_zip")
        response = requests.get(
        f'http://api.openweathermap.org/data/2.5/weather?zip={user_zip},us&appid=384549281a1b886956dff00758e198a3&units=imperial')
        res = response.json()
        home_name = res["name"]
        ends_with_s = home_name.endswith("s")
        home_temp = res['main']['temp']
        home_weath = res['weather'][0]['description']
        home_feels_like = res['main']['feels_like']
        home_temp_min = res['main']['temp_min']
        home_temp_max = res['main']['temp_max']
        home_wind_speed = res['wind']['speed']
        return render_template('home.html', top_locs=top_locs, home_weath=home_weath, home_temp=home_temp, home_name=home_name, home_feels_like=home_feels_like, home_temp_min=home_temp_min, home_temp_max=home_temp_max, home_wind_speed=home_wind_speed, user_zip=user_zip, ends_with_s=ends_with_s)
    return render_template('home.html', top_locs=top_locs)

@app.route("/editprofile", methods=["GET", "POST"])
def profile_edit():
    form = ProfileEditForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=session["username"]).one()
            if user:
                old_user = user.username
            User.update(
                old_username=old_user,
                username=form.username.data,
                password1=form.password1.data,
                password2=form.password2.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
                zip_code=form.zip_code.data or None
            )
            do_update(user)
            db.session.commit()
            return redirect('/editprofile')
        except IntegrityError:
            flash("Passwords don't match", 'danger')
            return render_template('users/update.html', form=form)
    else:
        return render_template('users/update.html', form=form)

@app.route('/location')
def get_weather():
    zip_code = request.args['search']

    response = requests.get(
        f'http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid=384549281a1b886956dff00758e198a3&units=imperial')
    weather_info = response.json()

    location = weather_info['name']
    exists = Location.query.filter_by(zip_code=zip_code).first()
    if not exists:
        new_loc = Location(name=location, zip_code=zip_code)
        db.session.add(new_loc)
        db.session.commit()
        return redirect(f'/location/{new_loc.zip_code}')
    else:
        ex_loc = Location.query.filter_by(name=location).first()
        return redirect(f'/location/{ex_loc.zip_code}')


@app.route('/location/<int:zip_code>')
def display_loc(zip_code):
    response = requests.get(
        f'http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid=384549281a1b886956dff00758e198a3&units=imperial')
    res = response.json()
    name = res['name']
    ends_with_s = name.endswith("s")
    temp = res['main']['temp']
    weath = res['weather'][0]['description']
    feels_like = res['main']['feels_like']
    temp_min = res['main']['temp_min']
    temp_max = res['main']['temp_max']
    wind_speed = res['wind']['speed']
    humidity = res['main']['humidity']
    visibility = res['visibility']

    existing_loc = Location.query.filter_by(zip_code=zip_code).first()
    existing_loc.times_searched = existing_loc.times_searched + 1
    return render_template('location.html', existing_loc=existing_loc, temp=temp, weath=weath, feels_like=feels_like, temp_min=temp_min, temp_max=temp_max, wind_speed=wind_speed, humidity=humidity, visibility=visibility, ends_with_s=ends_with_s)
