from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

doctor = Blueprint("doctor", __name__)


@doctor.route("/dashboard/doctor")
@login_required
def dashboard():
    if current_user.role != "Doctor":
        abort(403)

    flash("Page loaded successfully!", category="info")
    return render_template("doctor/dashboard.html")


@doctor.route("/dashboard/doctor/profile")
@login_required
def profile():
    if current_user.role != "Doctor":
        abort(403)

    return render_template("doctor/profile.html")

