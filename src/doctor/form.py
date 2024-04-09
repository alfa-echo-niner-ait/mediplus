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
