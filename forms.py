from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')
    location = StringField('(Optional) Zip Code', validators=[Length(max=5)])

class ProfileEditForm(FlaskForm):
    """Form to edit your profile."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password1 = PasswordField('Password', validators=[Length(min=6)])
    password2 = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')
    zip_code = StringField('(Optional) Zip Code', validators=[Length(max=5)])