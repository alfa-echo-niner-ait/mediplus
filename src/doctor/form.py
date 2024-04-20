from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    SelectField,
    SubmitField,
    DateField,
    PasswordField,
    StringField,
    DecimalField,
    TextAreaField,
    SelectMultipleField,
)
from wtforms.validators import DataRequired, EqualTo, Length
from datetime import date


class UpdateProfileForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    gender = SelectField(
        "Gender",
        validators=[DataRequired()],
        choices=[("Male", "Male"), ("Female", "Female")],
    )
    birthdate = DateField("Birth Date", validators=[DataRequired()], default=date.today)
    phone = StringField("Phone", validators=[DataRequired()])
    email = StringField("Email Address", validators=[DataRequired()])
    avatar = FileField(
        "Change Avatar",
        validators=[
            FileAllowed(["jpg", "jpeg", "png", "svg"], "Please pick correct format!")
        ],
    )

    submit = SubmitField("Update Profile")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            EqualTo("confirm_password", "Password didn't match!"),
        ],
    )
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])

    submit = SubmitField("Change Password")


class UpdateScheduleForm(FlaskForm):
    days = SelectMultipleField(
        "Select Available Days",
        validators=[DataRequired()],
        choices=[
            (6, "Saturday"),
            (0, "Sunday"),
            (1, "Monday"),
            (2, "Tuesday"),
            (3, "Wednesday"),
            (4, "Thursday"),
            (5, "Friday"),
        ],
    )
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
    submit = SubmitField("Update Schedule")
