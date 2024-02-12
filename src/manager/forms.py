from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, DateField, PasswordField, StringField
from wtforms.validators import DataRequired, EqualTo
from datetime import date


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("new_password")]
    )

    submit = SubmitField("Change Password")


class LogSortForm(FlaskForm):
    role = SelectField(
        "Role",
        validators=[DataRequired()],
        choices=[
            ("All", "All"),
            ("Patient", "Patients"),
            ("Doctor", "Doctors"),
            ("Manager", "Managers"),
        ],
    )
    order = SelectField(
        "Order By",
        validators=[DataRequired()],
        choices=[("desc", "New First"), ("asc", "Old First")],
    )
    date = DateField("Date", validators=[DataRequired()], default=date.today)

    count = SelectField(
        "Per Page",
        validators=[DataRequired()],
        choices=[
            (12, "12"),
            (15, "15"),
            (20, "20"),
            (25, "25"),
            (30, "30"),
            (40, "40"),
            (50, "50"),
            (60, "60"),
            (70, "70"),
            (80, "80"),
            (90, "90"),
            (100, "100"),
        ],
    )

    submit = SubmitField("Show")


class SelfProfileForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    gender = SelectField(
        "Gender",
        validators=[DataRequired()],
        choices=[("Male", "Male"), ("Female", "Female")],
    )
    birthdate = DateField("Birth Date", validators=[DataRequired()])
    email = StringField("Email Address", validators=[DataRequired()])
    phone = StringField("Phone Number", validators=[DataRequired()])

    submit = SubmitField("Update Profile")
