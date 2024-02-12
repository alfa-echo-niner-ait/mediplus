from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from src.users.models import Users, User_Logs, Patients, Doctors, Managers
from .forms import LogSortForm, ChangePasswordForm, SelfProfileForm
from src import db, hash_manager
from src.public.utils import get_datetime


manager = Blueprint("manager", __name__)


@manager.route("/dashboard/manager")
@login_required
def dashboard():
    return render_template("manager/dashboard.html", title="Manager Dashboard")


@manager.route("/dashboard/manager/managers")
@login_required
def managers():
    page_num = request.args.get("page", 1, int)

    managers = (
        Managers.query.join(Users, Managers.m_id == Users.id)
        .add_columns(
            Users.id,
            Users.username,
            Users.email,
            Users.gender,
            Managers.first_name,
            Managers.last_name,
            Managers.phone,
            Managers.avatar,
        )
        .order_by(Managers.m_id.desc())
        .paginate(page=page_num, per_page=12)
    )

    return render_template("manager/managers.html", managers=managers, title="Managers")


@manager.route("/dashboard/manager/doctors")
@login_required
def doctors():
    return render_template("manager/doctors.html", title="Doctors")


# Patients
@manager.route("/dashboard/manager/patients")
@login_required
def patients():
    page_num = request.args.get("page", 1, int)

    patients = (
        Patients.query.join(Users, Patients.p_id == Users.id)
        .add_columns(
            Users.id,
            Users.username,
            Users.email,
            Users.gender,
            Patients.first_name,
            Patients.last_name,
            Patients.birthdate,
            Patients.avatar,
        )
        .order_by(Patients.p_id.desc())
        .paginate(page=page_num, per_page=15)
    )
    return render_template("manager/patients.html", title="Patients", patients=patients)


# Activity Logs
@manager.route("/dashboard/manager/logs", methods=["GET", "POST"])
@login_required
def logs():
    page_num = request.args.get("page", 1, int)

    form = LogSortForm()
    logs = (
        User_Logs.query.join(Users, User_Logs.user_id == Users.id)
        .order_by(User_Logs.log_id.desc())
        .add_columns(
            User_Logs.log_id,
            User_Logs.user_id,
            User_Logs.log_type,
            User_Logs.log_date,
            User_Logs.log_time,
            Users.username,
            Users.role,
        )
        .paginate(page=page_num, per_page=12)
    )

    if form.validate_on_submit():
        role = form.role.data
        date = form.date.data
        order = form.order.data
        count = int(form.count.data)

        # New first order
        if order == "desc":
            if role == "All":
                logs = (
                    User_Logs.query.join(Users, User_Logs.user_id == Users.id)
                    .filter(User_Logs.log_date == date)
                    .order_by(User_Logs.log_id.desc())
                    .add_columns(
                        User_Logs.log_id,
                        User_Logs.user_id,
                        User_Logs.log_type,
                        User_Logs.log_date,
                        User_Logs.log_time,
                        Users.username,
                        Users.role,
                    )
                    .paginate(page=page_num, per_page=count)
                )

                return render_template(
                    "manager/logs.html", title="Activity Logs", logs=logs, form=form
                )
            else:
                logs = (
                    User_Logs.query.join(Users, User_Logs.user_id == Users.id)
                    .filter(Users.role == role, User_Logs.log_date == date)
                    .order_by(User_Logs.log_id.desc())
                    .add_columns(
                        User_Logs.log_id,
                        User_Logs.user_id,
                        User_Logs.log_type,
                        User_Logs.log_date,
                        User_Logs.log_time,
                        Users.username,
                        Users.role,
                    )
                    .paginate(page=page_num, per_page=count)
                )

                return render_template(
                    "manager/logs.html", title="Activity Logs", logs=logs, form=form
                )

        # Old first order
        else:
            if role == "All":
                logs = (
                    User_Logs.query.join(Users, User_Logs.user_id == Users.id)
                    .filter(User_Logs.log_date == date)
                    .order_by(User_Logs.log_id)
                    .add_columns(
                        User_Logs.log_id,
                        User_Logs.user_id,
                        User_Logs.log_type,
                        User_Logs.log_date,
                        User_Logs.log_time,
                        Users.username,
                        Users.role,
                    )
                    .paginate(page=page_num, per_page=count)
                )

                return render_template(
                    "manager/logs.html", title="Activity Logs", logs=logs, form=form
                )
            else:
                logs = (
                    User_Logs.query.join(Users, User_Logs.user_id == Users.id)
                    .filter(Users.role == role, User_Logs.log_date == date)
                    .order_by(User_Logs.log_id)
                    .add_columns(
                        User_Logs.log_id,
                        User_Logs.user_id,
                        User_Logs.log_type,
                        User_Logs.log_date,
                        User_Logs.log_time,
                        Users.username,
                        Users.role,
                    )
                    .paginate(page=page_num, per_page=count)
                )

                return render_template(
                    "manager/logs.html", title="Activity Logs", logs=logs, form=form
                )

    return render_template(
        "manager/logs.html", title="Activity Logs", logs=logs, form=form
    )


@manager.route("/dashboard/manager/account", methods=["GET", "POST"])
@login_required
def account():
    page_num = request.args.get("page", 1, int)
    
    form = SelfProfileForm()
    user: Users = Users.query.filter_by(id=current_user.id).first()
    profile: Managers = Managers.query.filter_by(m_id=current_user.id).first()

    logs = (
        User_Logs.query.filter_by(user_id=current_user.id)
        .order_by(User_Logs.log_id.desc())
        .paginate(page=page_num, per_page=10)
    )
    
    if form.validate_on_submit():
        profile.first_name = form.first_name.data
        profile.last_name = form.last_name.data
        user.gender = form.gender.data
        user.email = form.email.data
        profile.phone = form.phone.data
        profile.birthdate = form.birthdate.data
        
        date, time = get_datetime()
        new_log = User_Logs(current_user.id, "Update Profile", date, time)
        db.session.add(new_log)
        db.session.commit()

        flash("Profile Updated Successfully!", category="success")
        return redirect(url_for('manager.account'))

    elif request.method == 'GET':
        form.first_name.data = profile.first_name
        form.last_name.data = profile.last_name
        form.gender.data = user.gender
        form.email.data = user.email
        form.phone.data = profile.phone
        form.birthdate.data = profile.birthdate
        
    return render_template("manager/account.html", title="My Account", logs=logs, form=form)


# Self Change Password
@manager.route("/dashboard/manager/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        current_password = form.current_password.data
        if hash_manager.check_password_hash(
            current_user.password_hash, current_password
        ):
            new_password = form.confirm_password.data
            password_hash = hash_manager.generate_password_hash(new_password).decode(
                "utf-8"
            )

            user = Users.query.filter_by(id=current_user.id).first()
            user.password_hash = password_hash

            date, time = get_datetime()
            new_log = User_Logs(current_user.id, "Change Password", date, time)
            db.session.add(new_log)
            db.session.commit()

            flash("Password changed successfully!", category="success")
            return redirect(url_for("manager.dashboard"))
        else:
            flash("Sorry, current password didn't match!", category="danger")

    return render_template(
        "manager/change_password.html", form=form, title="Change Password"
    )
