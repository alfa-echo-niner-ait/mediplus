from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    SelectField,
    BooleanField,
    SubmitField,
    DateField,
)
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo
from datetime import date


class LoginForm(FlaskForm):
    account = StringField(
        "Account", validators=[DataRequired(), Length(min=2, max=50)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    login_with = SelectField(
        "Login With",
        validators=[DataRequired()],
        choices=[("username", "Username"), ("email", "Email")],
    )
    remember = BooleanField("Keep Me Logged In")

    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=50)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), EqualTo("re_password", "Password didn't match!")]
    )
    re_password = PasswordField(
        "Confirm Password", validators=[DataRequired()]
    )
    email = StringField("Email Address", validators=[DataRequired()])
    gender = SelectField(
        "Gender",
        validators=[DataRequired()],
        choices=[("Male", "Male"), ("Female", "Female")],
    )
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    birthdate = DateField("Birth Date", validators=[DataRequired()], default=date.today)

    submit = SubmitField("Register")


class ResetRequestForm(FlaskForm):
    email = StringField("Account Email", validators=[DataRequired()])
    submit = SubmitField("Reset Request")


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "New Password", validators=[DataRequired(), EqualTo("re_password", "Password didn't match!")]
    )
    re_password = PasswordField(
        "Confirm Password", validators=[DataRequired()]
    )
    submit = SubmitField("Change Password")

class SearchTestForm(FlaskForm):
    keyword = StringField("Test Name", validators=[DataRequired()])
    submit = SubmitField("Search")

class SearchDoctorForm(FlaskForm):
    keyword = StringField("Doctor Name/Speciality", validators=[DataRequired()])
    submit = SubmitField("Search")
