from flask import Blueprint, render_template
from flask_login import login_required

doctor = Blueprint("doctor", __name__)


@doctor.route("/dashboard/doctor")
@login_required
def dashboard():
    return render_template("doctor/dashboard.html")
