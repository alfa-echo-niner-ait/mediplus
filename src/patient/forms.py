from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
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


class UpdateProfileForm(FlaskForm):
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
    avatar = FileField(
        "Update Display Picture",
        validators=[
            FileAllowed(["jpg", "jpeg", "png", "svg"], "Please pick correct format!")
        ],
    )

    submit = SubmitField("Update Profile")
