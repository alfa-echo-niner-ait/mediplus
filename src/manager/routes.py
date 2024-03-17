from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    session,
    abort,
)
from flask_login import login_required, current_user
from src.users.models import Users, User_Logs, Patients, Doctors, Managers
from src.patient.models import Invoices, Invoice_Items, Payments, Medical_Tests
from .forms import (
    LogSortForm,
    ChangePasswordForm,
    SelfProfileForm,
    NewMedicalTestForm,
    UpdateMedicalTestForm,
)
from src import db, hash_manager
from src.public.utils import (
    get_datetime,
    profile_picture_saver,
    profile_picture_remover,
)


manager = Blueprint("manager", __name__)


@manager.route("/dashboard/manager")
@login_required
def dashboard():
    return render_template("manager/dashboard.html", title="Manager Dashboard")


@manager.route("/dashboard/appointments")
@login_required
def appointemnts():
    return render_template("manager/appointments.html", title="Appointments Management")


@manager.route("/dashboard/tests", methods=["GET", "POST"])
@login_required
def tests():
    new_test_form = NewMedicalTestForm()

    if new_test_form.validate_on_submit():
        date, time = get_datetime()
        new_test = Medical_Tests(
            new_test_form.test_name.data,
            new_test_form.test_price.data,
            date,
            time,
            new_test_form.test_desc.data,
        )
        db.session.add(new_test)

        new_log = User_Logs(current_user.id, "Create New Test", date, time)
        new_log.log_desc = f"Name: {new_test_form.test_name.data}, Price: {new_test_form.test_price.data}"
        db.session.add(new_log)
        # Commit to the database
        db.session.commit()

        flash("New Test Added to the Catalog!", category="success")
        return redirect(url_for("manager.tests"))

    return render_template(
        "manager/tests.html", new_test_form=new_test_form, title="Tests Management"
    )


@manager.route("/dashboard/manager/tests/catalog")
@login_required
def test_catalog():
    page_num = request.args.get("page", 1, int)
    tests = Medical_Tests.query.order_by(Medical_Tests.test_name.asc()).paginate(
        page=page_num, per_page=12
    )

    return render_template(
        "manager/test_catalog.html", tests=tests, title="Test Catalog"
    )


@manager.route("/dashboard/manager/tests/catalog/<test_id>", methods=["GET", "POST"])
@login_required
def view_test(test_id):
    form = UpdateMedicalTestForm()
    test: Medical_Tests = Medical_Tests.query.filter_by(test_id=test_id).first_or_404()

    if form.validate_on_submit():
        test.test_name = form.test_name.data
        test.test_price = form.test_price.data
        test.test_desc = form.test_desc.data

        date, time = get_datetime()
        new_log = User_Logs(current_user.id, "Update Test", date, time)
        new_log.log_desc = f"#{test.test_id} {test.test_name}"
        db.session.add(new_log)
        db.session.commit()

        flash("Test Updated Successfully!", category="success")
        return redirect(url_for("manager.view_test", test_id=test_id))
    elif request.method == "GET":
        form.test_name.data = test.test_name
        form.test_price.data = test.test_price
        form.test_desc.data = test.test_desc

    return render_template(
        "manager/view_test.html", test=test, form=form, title=test.test_name
    )


@manager.route("/dashboard/manager/tests/delete/<test_id>")
@login_required
def delete_test(test_id):
    if current_user.role == "Manager":
        test: Medical_Tests = Medical_Tests.query.filter_by(
            test_id=test_id
        ).first_or_404()
        db.session.delete(test)

        date, time = get_datetime()
        new_log = User_Logs(current_user.id, "Delete Test", date, time)
        new_log.log_desc = f"#{test.test_id} {test.test_name} ({test.test_price})"
        db.session.add(new_log)
        # Commit to the database
        db.session.commit()

        flash("Test deleted successfully!", category="warning")
        return redirect(url_for("manager.test_catalog"))
    else:
        abort(403)


@manager.route("/dashboard/invoices")
@login_required
def invoices():
    page_num = request.args.get("page", 1, int)

    invoices = (
        Invoices.query.join(Patients, Invoices.invoice_patient_id == Patients.p_id)
        .order_by(Invoices.invoice_id.desc())
        .add_columns(
            Patients.p_id,
            Patients.first_name,
            Patients.last_name,
            Patients.phone,
            Invoices.invoice_id,
            Invoices.total_amount,
            Invoices.status,
            Invoices.invoice_date,
            Invoices.invoice_time,
        )
        .paginate(page=page_num, per_page=12)
    )

    return render_template(
        "manager/invoices.html", title="Invoices Management", invoices=invoices
    )


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


@manager.route("/dashboard/manager/logs/<id>")
@login_required
def log_details(id):
    log = (
        User_Logs.query.filter_by(log_id=int(id))
        .join(Users, User_Logs.user_id == Users.id)
        .add_columns(
            Users.id,
            Users.username,
            Users.email,
            Users.role,
            User_Logs.log_id,
            User_Logs.log_type,
            User_Logs.log_date,
            User_Logs.log_time,
            User_Logs.log_type,
            User_Logs.log_desc,
        )
        .first()
    )

    return render_template(
        "manager/log_details.html", title=f"Log #{id} Details", log=log
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
        avatar = ""
        if form.avatar.data:
            # Remove the old picture from the file system
            if profile.avatar != "manager.svg":
                profile_picture_remover(profile.avatar, "manager")

            # Store the new picture in the file system
            avatar = profile_picture_saver(form.avatar.data, "manager")
            profile.avatar = avatar
            session["avatar"] = avatar

        # Add new informaiton to the model
        profile.first_name = form.first_name.data
        profile.last_name = form.last_name.data
        user.gender = form.gender.data
        user.email = form.email.data
        profile.phone = form.phone.data
        profile.birthdate = form.birthdate.data

        date, time = get_datetime()
        new_log = User_Logs(current_user.id, "Update Profile", date, time)
        db.session.add(new_log)
        # Commit to the database
        db.session.commit()

        flash("Profile Updated Successfully!", category="success")
        return redirect(url_for("manager.account"))

    elif request.method == "GET":
        form.first_name.data = profile.first_name
        form.last_name.data = profile.last_name
        form.gender.data = user.gender
        form.email.data = user.email
        form.phone.data = profile.phone
        form.birthdate.data = profile.birthdate

    return render_template(
        "manager/account.html", title="My Account", logs=logs, form=form
    )


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
