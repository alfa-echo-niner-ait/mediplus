from flask import Blueprint, render_template
from flask_login import login_required

patient = Blueprint('patient', __name__)


@patient.route('/dashboard/patient')
@login_required
def dashboard():
    return render_template('patient/dashboard.html')
