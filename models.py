from email.mime import image
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    """User model for user login/signup"""

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(
        db.String(20),
        nullable=False,
        unique=True
    )
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png"
    )
    zip_code = db.Column(db.Integer)

    @classmethod
    def signup(cls, username, email, password, image_url, zip_code):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
            zip_code=zip_code,
        )

        db.session.add(user)
        return user

    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        """Register a new user """
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        user = cls(
            username=username,
            password=hashed_utf8,
            first_name=first_name,
            last_name=last_name,
            email=email
        )

        db.session.add(user)
        return user
    
    @classmethod
    def update(cls, old_username, username, password1, password2, email, image_url, zip_code):
        """Update already existing users details in the database"""
        user = User.query.filter_by(username=old_username).one()
        user.username = username
        if password1 == password2:
            hashed = bcrypt.generate_password_hash(password1)
            hashed_utf8 = hashed.decode("utf8")
            user.password = hashed_utf8
            
        user.email = email
        user.image_url = image_url
        user.zip_code = zip_code
        return "success"
        
    @classmethod
    def authenticate(cls, username, password):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False


class Location(db.Model):
    """locations are stored by search"""

    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    zip_code = db.Column(db.Integer, nullable=False)
    times_searched = db.Column(db.Integer, nullable=False, default=1)