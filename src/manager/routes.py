from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src.users.models import Users, User_Logs
from src.manager.forms import SortForm, ChangePasswordForm
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
    return render_template("manager/managers.html", title="Managers")


@manager.route("/dashboard/manager/doctors")
@login_required
def doctors():
    return render_template("manager/doctors.html", title="Doctors")


@manager.route("/dashboard/manager/patients")
@login_required
def patients():
    return render_template("manager/patients.html", title="Patients")


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


@manager.route("/dashboard/manager/logs", methods=["GET", "POST"])
@login_required
def logs():
    page_num = request.args.get("page", 1, int)

    form = SortForm()
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
