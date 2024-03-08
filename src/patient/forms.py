from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    SelectField,
    SubmitField,
    DateField,
    PasswordField,
    StringField,
    DecimalField,
)
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


class MedicalInfoForm(FlaskForm):
    blood_group = StringField("Blood Group", validators=[DataRequired()])
    height_cm = DecimalField("Height(CM)")
    weight_kg = DecimalField("Weight(KG)")
    allergies = StringField("Allergies")
    medical_conditions = StringField("Medical Conditions")
    submit = SubmitField("Update Information")


class Record_Upload_Form(FlaskForm):
    file_name = StringField("File Name", validators=[DataRequired()])
    file = FileField(
        "Pick a Record File",
        validators=[
            DataRequired(),
            FileAllowed(
                ["jpg", "jpeg", "png", "svg", "pdf"], "Please pick allowed format!"
            ),
        ],
    )
    submit = SubmitField("Upload New Record")
