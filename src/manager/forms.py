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
    avatar = FileField(
        "Update Avatar",
        validators=[
            FileAllowed(["jpg", "jpeg", "png", "svg"], "Please pick correct format!")
        ],
    )

    submit = SubmitField("Update Profile")


class NewMedicalTestForm(FlaskForm):
    test_name = StringField("Test Name", validators=[DataRequired()])
    test_price = DecimalField("Test Price", validators=[DataRequired()])
    test_desc = TextAreaField("Test Description")
    submit = SubmitField("Add New Test")


class UpdateMedicalTestForm(FlaskForm):
    test_name = StringField("Test Name", validators=[DataRequired()])
    test_price = DecimalField("Test Price", validators=[DataRequired()])
    test_desc = TextAreaField("Test Description")
    submit = SubmitField("Update Test")


class UpdateInvoiceForm(FlaskForm):
    payment_amount = DecimalField("Total Amount", validators=[DataRequired()])
    payment_method = SelectField(
        "Payment Method",
        validators=[DataRequired()],
        choices=[("Cash", "Cash"), ("Online", "Online"), ("Other", "Other")],
    )
    payment_note = StringField("Payment Note")
    submit = SubmitField("Update")


class Test_Result_Upload_Form(FlaskForm):
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


class RegisterDoctorForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=50)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), EqualTo("confirm_password", "Password Didn't Match!")]
    )
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    email = StringField("Email Address", validators=[DataRequired()])
    gender = SelectField(
        "Gender",
        validators=[DataRequired()],
        choices=[("Male", "Male"), ("Female", "Female")],
    )
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    phone = StringField("Phone", validators=[DataRequired()])
    birthdate = DateField("Birth Date", validators=[DataRequired()], default=date.today)

    submit = SubmitField("Register")
