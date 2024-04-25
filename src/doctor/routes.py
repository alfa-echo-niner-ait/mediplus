from src import db, hash_manager
from src.public.utils import (
    get_datetime,
    profile_picture_remover,
    profile_picture_saver,
)
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    abort,
    request,
    jsonify,
)
from flask_login import login_required, current_user
from src.users.models import Users, User_Logs, Doctors, Patients
from src.doctor.models import Doctor_Time
from src.doctor.models import (
    Appointments,
    Appointment_Details,
    Prescriptions,
    Prescription_Extras,
    Prescribed_Items,
)
from src.doctor.form import (
    UpdateProfileForm,
    ChangePasswordForm,
    UpdateScheduleForm,
    PresItemForm,
    PresEditItemForm,
)


doctor = Blueprint("doctor", __name__)


@doctor.route("/dashboard/doctor")
@login_required
def dashboard():
    if current_user.role != "Doctor":
        abort(403)

    flash("Page loaded successfully!", category="info")
    return render_template("doctor/dashboard.html")


@doctor.route("/dashboard/doctor/appointments")
@login_required
def appointments():
    if current_user.role != "Doctor":
        abort(403)

    counts = {
        "pending": Appointments.query.filter(
            Appointments.appt_doctor_id == current_user.id
        )
        .join(Appointment_Details, Appointment_Details.appt_id == Appointments.appt_id)
        .filter(Appointment_Details.appt_status == "Booked")
        .count(),
        "accepted": Appointments.query.filter(
            Appointments.appt_doctor_id == current_user.id
        )
        .join(Appointment_Details, Appointment_Details.appt_id == Appointments.appt_id)
        .filter(Appointment_Details.appt_status == "Completed")
        .count(),
        "cancelled": Appointments.query.filter(
            Appointments.appt_doctor_id == current_user.id
        )
        .join(Appointment_Details, Appointment_Details.appt_id == Appointments.appt_id)
        .filter(Appointment_Details.appt_status == "Cancelled")
        .count(),
    }
    print(counts)
    return render_template(
        "doctor/appointments.html",
        counts=counts,
        appointments=appointments,
        title="Appointments",
    )


@doctor.route("/dashboard/doctor/appointments/<appt_id>/details")
@login_required
def appointment_view(appt_id):
    if current_user.role != "Doctor":
        abort(403)

    prescription_item_form = PresItemForm()
    edit_item_form = PresEditItemForm()
    appointment = (
        Appointments.query.filter(Appointments.appt_id == int(appt_id))
        .join(Appointment_Details, Appointments.appt_id == Appointment_Details.appt_id)
        .join(Patients, Appointments.appt_patient_id == Patients.p_id)
        .join(Prescriptions, Prescriptions.pres_appt_id == Appointments.appt_id)
        .join(Users, Patients.p_id == Users.id)
        .order_by(Appointment_Details.appt_date.asc())
        .add_columns(
            Appointments.appt_id,
            Appointment_Details.appt_status,
            Appointment_Details.appt_date,
            Appointment_Details.appt_time,
            Prescriptions.prescription_id,
            Users.gender,
            Patients.p_id,
            Patients.last_name,
            Patients.first_name,
            Patients.phone,
            Patients.birthdate,
            Patients.avatar,
        )
        .first_or_404()
    )

    return render_template(
        "doctor/appointment_view.html",
        appt=appointment,
        pitem_form=prescription_item_form,
        pedit_form=edit_item_form,
        title=f"Appointment #{appt_id} Details",
    )


@doctor.route("/dashboard/doctor/appointments/pending")
@login_required
def appointment_pending():
    if current_user.role != "Doctor":
        abort(403)

    page_num = request.args.get("page", 1, int)

    appointments = (
        Appointments.query.filter(Appointments.appt_doctor_id == current_user.id)
        .join(Appointment_Details, Appointments.appt_id == Appointment_Details.appt_id)
        .filter(Appointment_Details.appt_status == "Booked")
        .join(Patients, Appointments.appt_patient_id == Patients.p_id)
        .join(Users, Patients.p_id == Users.id)
        .order_by(Appointment_Details.appt_date.asc())
        .add_columns(
            Appointments.appt_id,
            Appointment_Details.appt_status,
            Appointment_Details.appt_date,
            Appointment_Details.appt_time,
            Users.gender,
            Patients.p_id,
            Patients.last_name,
            Patients.first_name,
            Patients.phone,
            Patients.birthdate,
            Patients.avatar,
        )
        .paginate(page=page_num, per_page=15)
    )

    return render_template(
        "doctor/appointments_pending.html",
        appointments=appointments,
        title="Pending Appointments",
    )


@doctor.route("/dashboard/doctor/appointments/accepted")
@login_required
def appointment_accepted():
    if current_user.role != "Doctor":
        abort(403)

    page_num = request.args.get("page", 1, int)

    appointments = (
        Appointments.query.filter(Appointments.appt_doctor_id == current_user.id)
        .join(Appointment_Details, Appointments.appt_id == Appointment_Details.appt_id)
        .filter(Appointment_Details.appt_status == "Completed")
        .join(Prescriptions, Prescriptions.pres_appt_id == Appointments.appt_id)
        .join(Patients, Appointments.appt_patient_id == Patients.p_id)
        .join(Users, Patients.p_id == Users.id)
        .order_by(Appointment_Details.appt_date.asc())
        .add_columns(
            Appointments.appt_id,
            Appointment_Details.appt_status,
            Appointment_Details.appt_date,
            Appointment_Details.appt_time,
            Prescriptions.prescription_id,
            Users.gender,
            Patients.p_id,
            Patients.last_name,
            Patients.first_name,
            Patients.phone,
            Patients.birthdate,
            Patients.avatar,
        )
        .paginate(page=page_num, per_page=15)
    )

    return render_template(
        "doctor/appointments_accepted.html",
        appointments=appointments,
        title="Accepted Appointments",
    )


@doctor.route("/dashboard/doctor/appointments/cancelled")
@login_required
def appointment_cancelled():
    if current_user.role != "Doctor":
        abort(403)

    page_num = request.args.get("page", 1, int)

    appointments = (
        Appointments.query.filter(Appointments.appt_doctor_id == current_user.id)
        .join(Appointment_Details, Appointments.appt_id == Appointment_Details.appt_id)
        .filter(Appointment_Details.appt_status == "Cancelled")
        .join(Patients, Appointments.appt_patient_id == Patients.p_id)
        .join(Users, Patients.p_id == Users.id)
        .order_by(Appointment_Details.appt_date.asc())
        .add_columns(
            Appointments.appt_id,
            Appointment_Details.appt_status,
            Appointment_Details.appt_date,
            Appointment_Details.appt_time,
            Users.gender,
            Patients.p_id,
            Patients.last_name,
            Patients.first_name,
            Patients.phone,
            Patients.birthdate,
            Patients.avatar,
        )
        .paginate(page=page_num, per_page=15)
    )

    return render_template(
        "doctor/appointments_cancelled.html",
        appointments=appointments,
        title="Cacelled Appointments",
    )


@doctor.route("/dashboard/doctor/appointments/<appt_id>/accept_patient/<patient_id>")
@login_required
def accept_appointment(appt_id, patient_id):
    if current_user.role != "Doctor":
        abort(403)

    # Accept appointment
    appt_details: Appointment_Details = Appointment_Details.query.filter(
        Appointment_Details.appt_id == int(appt_id)
    ).first_or_404()
    appt_details.appt_status = "Completed"

    date, time = get_datetime()
    doctor_log: User_Logs = User_Logs(current_user.id, "Accept Appointment", date, time)
    doctor_log.log_desc = f"Appointment #{appt_details.appt_date}, Detail #{appt_details.appt_detail_id}, Patient #{patient_id}"
    db.session.add(doctor_log)

    # Initialize prescription for the appointment
    new_prescription = Prescriptions(appt_details.appt_id, date, date, time)
    db.session.add(new_prescription)
    db.session.commit()

    new_extras = Prescription_Extras(new_prescription.prescription_id)
    db.session.add(new_extras)
    db.session.commit()

    flash("Appointment Accepted, Continue to Prescribe.", category="success")
    return redirect(url_for("doctor.appointment_view", appt_id=appt_id))


@doctor.route("/dashboard/doctor/appointments/<appt_id>/cancel")
@login_required
def cancel_appointment(appt_id):
    if current_user.role != "Doctor":
        abort(403)

    appointment_details: Appointment_Details = Appointment_Details.query.filter(
        Appointment_Details.appt_id == int(appt_id)
    ).first_or_404()
    appointment_details.appt_status = "Cancelled"
    appointment: Appointments = Appointments.query.filter(
        Appointments.appt_id == int(appt_id)
    ).first()

    date, time = get_datetime()
    doctor_log: User_Logs = User_Logs(current_user.id, "Cancel Appointment", date, time)
    doctor_log.log_desc = f"Appointment #{appointment.appt_id}, Patient #{appointment.appt_patient_id} on {appointment_details.appt_date} ({appointment_details.appt_time})"
    db.session.add(doctor_log)

    patient_log: User_Logs = User_Logs(
        appointment.appt_patient_id, "Appointment Cancelled", date, time
    )
    patient_log.log_desc = (
        f"Doctor has cancelled your appointment. Try different date/time slot."
    )
    db.session.add(patient_log)

    db.session.commit()

    flash("Appointment has been cancelled!", category="warning")
    return redirect(url_for("doctor.appointment_pending"))


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
    user: Users = Users.query.filter(Users.id == current_user.id).first_or_404()
    doctor: Doctors = Doctors.query.filter(
        Doctors.d_id == current_user.id
    ).first_or_404()

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
        new_log.log_desc = f"""Doctor #{current_user.id} @ {user.username}
        IP: {request.remote_addr}
        Device: {request.headers.get("User-Agent")}
        """
        db.session.add(new_log)
        db.session.commit()

        flash("Profile Updated Successfully!", category="success")
        return redirect(url_for("doctor.profile"))
    else:
        flash("Profile Update Failed!", category="danger")
        return redirect(url_for("doctor.profile"))


@doctor.route("/dashboard/doctor/schedule", methods=["GET", "POST"])
@login_required
def update_schedule():
    if current_user.role != "Doctor":
        abort(403)

    doctor_time: Doctor_Time = Doctor_Time.query.filter(
        Doctor_Time.doctor_id == current_user.id
    ).first()

    day_time_slot = doctor_time.day_time_slot

    form = UpdateScheduleForm()

    if request.method == "GET" and day_time_slot:
        # Convert string to int and set to form
        form.days.data = [int(day) for day in day_time_slot.get("days", [])]
        form.times.data = day_time_slot["times"]

    elif form.validate_on_submit() and request.method == "POST":
        if day_time_slot:
            copy = dict(day_time_slot)
            copy["days"] = form.days.data
            copy["times"] = form.times.data

            doctor_time.day_time_slot = copy
        else:
            days = form.days.data
            times = form.times.data

            new_day_time_slot = dict()
            new_day_time_slot["days"] = days
            new_day_time_slot["times"] = times

            doctor_time.day_time_slot = new_day_time_slot

        date, time = get_datetime()
        new_log = User_Logs(current_user.id, "Update Schedule", date, time)
        db.session.add(new_log)
        db.session.commit()

        flash("Schedule Updated Successfully!", category="success")
        return redirect(url_for("doctor.update_schedule"))

    elif request.method == "POST":
        flash("Empty field can't be accepted!", category="warning")
        return redirect(url_for("doctor.update_schedule"))

    return render_template(
        "doctor/update_schedule.html",
        form=form,
        title="Update Schedule",
    )


@doctor.route("/dashboard/doctor/profile/update/password", methods=["POST"])
@login_required
def change_password_handler():
    if current_user.role != "Doctor":
        abort(403)

    password_form = ChangePasswordForm()
    if password_form.validate_on_submit():
        if hash_manager.check_password_hash(
            current_user.password_hash, password_form.current_password.data
        ):
            user: Users = Users.query.filter(Users.id == current_user.id).first_or_404()

            password_hash = hash_manager.generate_password_hash(
                password_form.new_password.data
            ).decode("utf-8")
            user.password_hash = password_hash

            date, time = get_datetime()
            new_log = User_Logs(current_user.id, "Change Password", date, time)
            new_log.log_desc = f"""Doctor #{current_user.id} @ {user.username}
            IP: {request.remote_addr}
            Device: {request.headers.get("User-Agent")}
            """
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


@doctor.route(
    "/dashboard/doctor/prescription/<prescription_id>/add_pitem", methods=["POST"]
)
@login_required
def add_prescription_item(prescription_id):
    form = PresItemForm()

    date, time = get_datetime()
    prescription: Prescriptions = Prescriptions.query.filter(
        Prescriptions.prescription_id == int(prescription_id)
    ).first()
    prescription.last_update_date = date
    prescription.last_update_time = time

    new_item: Prescribed_Items = Prescribed_Items(
        prescription_id,
        form.item_medicine.data,
        form.item_dosage.data,
        form.item_instruction.data,
        form.item_duration.data,
    )
    db.session.add(new_item)
    db.session.commit()

    res_data = {
        "result": "success",
        "id": new_item.pres_item_id,
        "medicine": new_item.medicine,
        "dosage": new_item.dosage,
        "instruction": new_item.instruction,
        "duration": new_item.duration,
    }

    return jsonify(res_data)


@doctor.route(
    "/dashboard/doctor/prescription/<prescription_id>/edit_pitem/<item_id>",
    methods=["POST"],
)
@login_required
def edit_prescription_item(prescription_id, item_id):
    form = PresEditItemForm()
    item: Prescribed_Items = Prescribed_Items.query.filter(
        Prescribed_Items.pres_item_id == int(item_id)
    ).first()

    item.medicine = form.edit_medicine.data
    item.dosage = form.edit_dosage.data
    item.instruction = form.edit_instruction.data
    item.duration = form.edit_duration.data

    date, time = get_datetime()
    prescription: Prescriptions = Prescriptions.query.filter(
        Prescriptions.prescription_id == int(prescription_id)
    ).first()
    prescription.last_update_date = date
    prescription.last_update_time = time

    db.session.commit()

    res_data = {
        "result": "success",
        "id": item.pres_item_id,
        "medicine": item.medicine,
        "dosage": item.dosage,
        "instruction": item.instruction,
        "duration": item.duration,
    }

    return jsonify(res_data)


@doctor.route(
    "/dashboard/doctor/prescription/<prescription_id>/delete_pitem/<item_id>",
    methods=["DELETE"],
)
@login_required
def delete_prescription_item(prescription_id, item_id):
    item: Prescribed_Items = Prescribed_Items.query.filter(
        Prescribed_Items.pres_item_id == int(item_id)
    ).first()
    if item:
        db.session.delete(item)

        date, time = get_datetime()
        prescription: Prescriptions = Prescriptions.query.filter(
            Prescriptions.prescription_id == int(prescription_id)
        ).first()
        prescription.last_update_date = date
        prescription.last_update_time = time

        db.session.commit()
        return "success"


@doctor.route(
    "/dashboard/doctor/prescription/<prescription_id>/update/diagnosis",
    methods=["POST"],
)
@login_required
def update_prescription_diagnosis(prescription_id):
    extras: Prescription_Extras = Prescription_Extras.query.filter(
        Prescription_Extras.prescription_id == int(prescription_id)
    ).first()
    if extras:
        extras.diagnosis = request.form.get("diag")
        db.session.commit()
        return "success"


@doctor.route(
    "/dashboard/doctor/prescription/<prescription_id>/update/notes", methods=["POST"]
)
@login_required
def update_prescription_notes(prescription_id):
    extras: Prescription_Extras = Prescription_Extras.query.filter(
        Prescription_Extras.prescription_id == int(prescription_id)
    ).first()
    if extras:
        extras.notes = request.form.get("notes")
        db.session.commit()
        return "success"


@doctor.route(
    "/dashboard/doctor/prescription/<prescription_id>/update/nextmeet", methods=["POST"]
)
@login_required
def update_prescription_nextmeet(prescription_id):
    extras: Prescription_Extras = Prescription_Extras.query.filter(
        Prescription_Extras.prescription_id == int(prescription_id)
    ).first()
    if extras:
        extras.next_meet = request.form.get("meet")
        db.session.commit()
        return "success"
