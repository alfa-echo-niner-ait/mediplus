from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required

manager = Blueprint('manager', __name__)

@manager.route('/dashboard')
@login_required
def dashboard():
    flash("Welcome to dashboard", category="info")
    return render_template('manager/dashboard.html')