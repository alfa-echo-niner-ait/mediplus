from flask import Blueprint, render_template
from flask_login import login_required, current_user
from src.users.models import Users, Patients


patient = Blueprint("patient", __name__)


@patient.route("/dashboard/patient")
@login_required
def dashboard():
    user = (
        Patients.query.join(Users, Patients.p_id == Users.id)
        .filter(Patients.p_id == current_user.id)
        .add_columns(
            Users.username,
            Users.gender,
            Users.email,
            Patients.first_name,
            Patients.last_name,
            Patients.phone,
            Patients.birthdate,
            Patients.avatar,
        )
        .first()
    )
    
    return render_template("patient/dashboard.html", user=user)
