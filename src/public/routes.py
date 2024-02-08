from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    current_app,
    flash,
    request,
)
from flask_login import current_user, login_user, login_required, logout_user
from .forms import LoginForm, RegisterForm, ResetRequestForm, ResetPasswordForm
from .utils import get_datetime
from src.users.models import Users, Patients, User_Logs, Medical_Info
from src.users.utils import reset_mail_sender
from src import db, token_manager, hash_manager

public = Blueprint("public", __name__)


@public.route("/", methods=["GET", "POST"])
def index():
    return render_template("public/index.html")


@public.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        user = Users.query.filter_by(username=username).first()
        if user and hash_manager.check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            date, time = get_datetime()

            new_log = User_Logs(current_user.id, "Login", date, time)
            db.session.add(new_log)
            db.session.commit()
            flash("Login successfull!", category="info")
            return redirect(url_for("public.index"))

    return render_template("public/login.html", form=form, title="Login")


@public.route("/logout")
def logout():
    date, time = get_datetime()
    new_log = User_Logs(current_user.id, "Logout", date, time)
    db.session.add(new_log)
    db.session.commit()

    logout_user()
    flash("Logout successfull!", category="warning")
    return redirect(url_for("public.index"))


@public.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        gender = form.gender.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        birthdate = form.birthdate.data

        avatar = "user_male.svg" if gender == "Male" else "user_female.svg"
        password_hash = hash_manager.generate_password_hash(password).decode("utf-8")
        date, time = get_datetime()

        new_user = Users(username, password_hash, email, gender, "Patient")
        db.session.add(new_user)
        db.session.commit()

        user = Users.query.filter_by(username=username).first()
        new_patient = Patients(user.id, first_name, last_name, birthdate, avatar)
        new_log = User_Logs(user.id, "Registration", date, time)
        db.session.add(new_patient)
        db.session.add(new_log)
        db.session.commit()

        patient = Patients.query.filter_by(p_id=user.id).first()
        new_info = Medical_Info(patient.p_id)
        db.session.add(new_info)
        db.session.commit()

        flash("Registration successfull! Login to continue.", category="success")
        return redirect(url_for("public.login"))

    return render_template("public/register.html", form=form, title="Registration")


@public.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    form = ResetRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        user = Users.query.filter_by(email=email).first()
        print(f"\n{user}\n")
        if user:
            token = token_manager.sign(f"{user.role}{user.email}{user.id}").decode(
                "utf-8"
            )
            user.token = token
            db.session.commit()
            reset_mail_sender(user)
            flash("Password reset link sent to your email!", category="success")
        else:
            flash("Sorry, no user found with this email!", category="warning")
        return redirect(url_for("public.reset_request"))

    return render_template(
        "public/reset_request.html", form=form, title="Reset Password"
    )


@public.route("/reset_password/<username>/<token>", methods=["GET", "POST"])
def reset_password(username, token):
    form = ResetPasswordForm()
    user = Users.query.filter_by(username=username).first()
    if request.method == "GET":
        if user and user.validate_token(token):
            return render_template(
                "public/reset_password.html", form=form, title="Change Password"
            )
        else:
            flash("Reset link error or timedout! Please try again!", category="danger")
            return redirect(url_for("public.reset_request"))

    if request.method == "POST":
        if form.validate_on_submit():
            password = form.password.data
            password_hash = hash_manager.generate_password_hash(password).decode(
                "utf-8"
            )

            user.password_hash = password_hash
            user.token = ""

            date, time = get_datetime()
            new_log = User_Logs(user.id, "Change Password", date, time)
            db.session.add(new_log)
            db.session.commit()

            flash(
                "Password changed successfully! Login to continue.", category="success"
            )
            return redirect(url_for("public.login"))


@public.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "Patient":
        return redirect(url_for("patient.dashboard"))
    elif current_user.role == "Doctor":
        return redirect(url_for("doctor.dashboard"))
    elif current_user.role == "Manager":
        return redirect(url_for("manager.dashboard"))
