from src import db, hash_manager
from src.public.utils import get_datetime, profile_picture_remover, profile_picture_saver
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from src.users.models import Users, User_Logs, Doctors
from src.doctor.form import UpdateProfileForm, ChangePasswordForm


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

    doctor = (
        Doctors.query.filter(Doctors.d_id == current_user.id)
        .join(Users, Doctors.d_id == Users.id)
        .add_columns(
            Users.gender,
            Users.email,
            Doctors.d_id,
            Doctors.first_name,
            Doctors.last_name,
            Doctors.title,
            Doctors.phone,
            Doctors.birthdate,
            Doctors.avatar,
        )
        .first_or_404()
    )
    form = UpdateProfileForm()
    password_form = ChangePasswordForm()

    if request.method == "GET":
        form.title.data = doctor.title
        form.first_name.data = doctor.first_name
        form.last_name.data = doctor.last_name
        form.gender.data = doctor.gender
        form.birthdate.data = doctor.birthdate
        form.phone.data = doctor.phone
        form.email.data = doctor.email

    return render_template(
        "doctor/profile.html",
        form=form,
        password_form=password_form,
        doctor=doctor,
        title="Update Profile",
    )

@doctor.route("/dashboard/doctor/profile/update", methods=["POST"])
@login_required
def update_profile_handler():
    if current_user.role != "Doctor":
        abort(403)

    form = UpdateProfileForm()
    user:Users = Users.query.filter(Users.id == current_user.id).first_or_404()
    doctor: Doctors = Doctors.query.filter(Doctors.d_id == current_user.id).first_or_404()

    if form.validate_on_submit():
        avatar = ""
        if form.avatar.data:
            if (
                doctor.avatar == "doctor_male.png"
                or doctor.avatar == "doctor_female.png"
            ):
                avatar = profile_picture_saver(form.avatar.data, "doctor")
            else:
                # Remove the old picture from the file system
                profile_picture_remover(doctor.avatar, "doctor")
                # Store the new picture in the file system
                avatar = profile_picture_saver(form.avatar.data, "doctor")

            doctor.avatar = avatar

        user.email = form.email.data
        user.gender = form.gender.data
        doctor.title = form.title.data
        doctor.first_name = form.first_name.data
        doctor.last_name = form.last_name.data
        doctor.birthdate = form.birthdate.data
        doctor.phone = form.phone.data

        date, time = get_datetime()
        new_log = User_Logs(current_user.id, "Update Profile", date, time)
        new_log.log_desc = f"Doctor #{current_user.id} @ {user.username}, IP: {request.remote_addr}, Device: {
            request.headers.get("User-Agent")}"
        db.session.add(new_log)
        db.session.commit()

        flash("Profile Updated Successfully!", category="success")
        return redirect(url_for("doctor.profile"))
    else:
        flash("Profile Update Failed!", category="danger")
        return redirect(url_for("doctor.profile"))


@doctor.route("/dashboard/doctor/profile/update/password", methods=["POST"])
@login_required
def change_password_handler():
    if current_user.role != "Doctor":
        abort(403)

    password_form = ChangePasswordForm()
    if password_form.validate_on_submit():
        if hash_manager.check_password_hash(current_user.password_hash, password_form.current_password.data):
            user: Users = Users.query.filter(Users.id == current_user.id).first_or_404()

            password_hash = hash_manager.generate_password_hash(
                password_form.new_password.data
            ).decode("utf-8")
            user.password_hash = password_hash

            date, time = get_datetime()
            new_log = User_Logs(current_user.id, "Change Password", date, time)
            new_log.log_desc = f"Doctor #{current_user.id} @ {user.username}, IP: {request.remote_addr}, Device: {
            request.headers.get("User-Agent")}"
            db.session.add(new_log)

            db.session.commit()
            flash("Password Changed Successfully!", category="success")
            return redirect(url_for("doctor.profile"))
        else:
            flash("Current password didn't match!", category="danger")
            return redirect(url_for("doctor.profile"))

    else:
        flash("Password update failed!", category="danger")
        return redirect(url_for("doctor.profile"))


@doctor.route("/dashboard/doctor/logs")
@login_required
def logs():
    if current_user.role != "Doctor":
        abort(403)

    page_num = request.args.get("page", 1, int)
    logs = (
        User_Logs.query.filter_by(user_id=current_user.id)
        .order_by(User_Logs.log_id.desc())
        .paginate(page=page_num, per_page=12)
    )
    return render_template("doctor/logs.html", logs=logs, title="Activity Logs")

