from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    SelectField,
    BooleanField,
    SubmitField,
    DateField,
    SelectMultipleField,
)
from wtforms.validators import DataRequired, Length, ValidationError, ReadOnly, EqualTo
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


class AppointmentForm(FlaskForm):
    appt_date = DateField("Appointment Date", validators=[ReadOnly()])
    times = SelectMultipleField(
        "Select Time Slot",
        choices=[
            ("00-01", "00-01"),
            ("01-02", "01-02"),
            ("02-03", "02-03"),
            ("03-04", "03-04"),
            ("04-05", "04-05"),
            ("05-06", "05-06"),
            ("06-07", "06-07"),
            ("07-08", "07-08"),
            ("08-09", "08-09"),
            ("09-10", "09-10"),
            ("10-11", "10-11"),
            ("11-12", "11-12"),
            ("12-13", "12-13"),
            ("13-14", "13-14"),
            ("14-15", "14-15"),
            ("15-16", "15-16"),
            ("16-17", "16-17"),
            ("17-18", "17-18"),
            ("18-19", "18-19"),
            ("19-20", "19-20"),
            ("20-21", "20-21"),
            ("21-22", "21-22"),
            ("22-23", "22-23"),
            ("23-00", "23-00"),
        ],
    )
    submit = SubmitField("Book Appointment")
