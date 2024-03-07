from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from src.users.models import Users, Patients, User_Logs, Medical_Info
from src.patient.forms import ChangePasswordForm, UpdateProfileForm, MedicalInfoForm
from src import db, hash_manager
from src.public.utils import (
    get_datetime,
    profile_picture_saver,
    profile_picture_remover,
)


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

    return render_template("patient/dashboard.html", user=user, title="Dashboard")


@patient.route("/dashboard/patient/update_profile", methods=["GET", "POST"])
@login_required
def update_profile():
    form = UpdateProfileForm()
    user: Users = Users.query.filter_by(id=current_user.id).first()
    profile: Patients = Patients.query.filter_by(p_id=current_user.id).first()

    if form.validate_on_submit():
        avatar = ""
        if form.avatar.data:
            # Remove the old picture from the file system
            if profile.avatar != "user_male.svg" or profile.avatar != "user_female.svg":
                profile_picture_remover(profile.avatar, "patient")

            # Store the new picture in the file system
            avatar = profile_picture_saver(form.avatar.data, "patient")
            profile.avatar = avatar

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
        return redirect(url_for("patient.update_profile"))

    elif request.method == "GET":
        form.first_name.data = profile.first_name
        form.last_name.data = profile.last_name
        form.gender.data = user.gender
        form.email.data = user.email
        form.phone.data = profile.phone
        form.birthdate.data = profile.birthdate

    return render_template(
        "patient/update_profile.html",
        form=form,
        avatar=profile.avatar,
        title="Update Profile",
    )


@patient.route("/dashboard/patient/change_password", methods=["GET", "POST"])
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
            return redirect(url_for("patient.change_password"))
        else:
            flash("Sorry, current password didn't match!", category="danger")

    return render_template(
        "patient/change_password.html", form=form, title="Change Password"
    )


@patient.route("/dashboard/patient/medical_records", methods=["GET", "POST"])
@login_required
def medical_records():
    form = MedicalInfoForm()

    records: Medical_Info = Medical_Info.query.filter_by(
        patient_id=current_user.id
    ).first()

    if request.method == "POST":
        print(f"\nForm received: {form.blood_group.data}\n")
        records.blood_group = form.blood_group.data
        records.height_cm = form.height_cm.data
        records.weight_kg = form.weight_kg.data
        records.allergies = form.allergies.data
        records.medical_conditions = form.medical_conditions.data

        date, time = get_datetime()
        new_log = User_Logs(current_user.id, "Update Medical Info", date, time)
        new_log.log_desc = f"({form.blood_group.data}), ({form.height_cm.data} CM), ({form.weight_kg.data} KG),({form.allergies.data}), ({form.medical_conditions.data}))"
        db.session.add(new_log)
        # Commit to the database
        db.session.commit()

        flash("Information Updated Successfully!", category="success")
        return redirect(url_for("patient.medical_records"))

    elif request.method == "GET":
        form.blood_group.data = records.blood_group
        form.height_cm.data = records.height_cm
        form.weight_kg.data = records.weight_kg
        form.allergies.data = records.allergies
        form.medical_conditions.data = records.medical_conditions

    return render_template(
        "patient/medical_records.html", form=form, title="Medical Records"
    )
