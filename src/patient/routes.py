import os
import secrets
from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
    url_for,
    request,
    current_app,
    send_file,
    abort,
    session,
)
from flask_login import login_required, current_user
from src.users.models import Users, Patients, Doctors, Managers, User_Logs
from src.patient.models import (
    Medical_Info,
    Patient_Record_Files,
    Invoices,
    Invoice_Items,
    Payments,
    Pending_Items,
    Medical_Tests,
    Medical_Test_Book,
    Medical_Report_Files,
)
from src.patient.forms import (
    ChangePasswordForm,
    UpdateProfileForm,
    MedicalInfoForm,
    Record_Upload_Form,
)
from src.doctor.models import Appointments, Appointment_Details, Prescriptions
from src import db, hash_manager
from src.public.utils import (
    get_datetime,
    profile_picture_saver,
    profile_picture_remover,
)


patient = Blueprint(name="patient", import_name=__name__, url_prefix="/patient")


@patient.route("/dashboard")
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
    ip = request.remote_addr
    info = request.headers.get("User-Agent")

    return render_template(
        "patient/dashboard.html", user=user, ip=ip, info=info, title="Dashboard"
    )


@patient.route("/add_to_cart", methods=["POST"])
@login_required
def add_item_to_cart():
    test_id = request.form.get("test_id")
    item_name = request.form.get("item_name")
    item_price = float(request.form.get("item_price"))

    item = Pending_Items(test_id, current_user.id, item_name, item_price)
    db.session.add(item)
    db.session.commit()
    return "success"


# Show Pending Items to Create Invoice
@patient.route("/items", methods=["GET", "POST"])
@login_required
def pending_items():
    if session["pending_items"] == 0:
        return redirect(url_for("public.dashboard"))
    items = Pending_Items.query.filter_by(item_user_id=current_user.id).all()
    price_sum = sum(item.item_price for item in items)

    return render_template(
        "patient/pending_items.html",
        items=items,
        price_sum=price_sum,
        title="Create Invoice",
    )


@patient.route("/items/delete/<item_id>")
@login_required
def delete_pending_item(item_id):
    item: Pending_Items = Pending_Items.query.filter_by(item_id=item_id).first_or_404()
    if item.item_user_id != current_user.id:
        abort(403)

    db.session.delete(item)
    db.session.commit()

    total_items = Pending_Items.query.filter_by(item_user_id=current_user.id).count()
    session["pending_items"] = total_items
    if total_items == 0:
        flash("Invoice Closed, No Items Left!", category="info")
        return redirect(url_for("public.dashboard"))
    else:
        flash("Item Removed Successfully!", category="warning")
        return redirect(url_for("patient.pending_items"))


@patient.route("/create_invoice")
@login_required
def create_invoice():
    if session["pending_items"] == 0:
        flash("Invoice Closed, No Items Left!", category="info")
        return redirect(url_for("public.dashboard"))

    date, time = get_datetime()
    items: Pending_Items = Pending_Items.query.filter_by(
        item_user_id=current_user.id
    ).all()

    new_invoice = Invoices(current_user.id, "Unpaid", date, time)
    db.session.add(new_invoice)
    db.session.commit()

    new_log = User_Logs(current_user.id, "Create New Invoice", date, time)
    new_log.log_desc = f"New Invoice ID: {new_invoice.invoice_id}"
    db.session.add(new_log)

    for item in items:
        new_invoice_item = Invoice_Items(
            new_invoice.invoice_id, item.item_test_id, item.item_desc, item.item_price
        )
        db.session.add(new_invoice_item)
        db.session.commit()

        new_test_book_item = Medical_Test_Book(
            new_invoice_item.item_id, current_user.id
        )
        db.session.add(new_test_book_item)
        db.session.delete(item)

    # Commit to the database
    db.session.commit()

    session["pending_items"] = 0
    flash("Invoice Created Successfully!", category="success")
    return redirect(url_for("patient.invoices"))


@patient.route("/dashboard/update_profile", methods=["GET", "POST"])
@login_required
def update_profile():
    form = UpdateProfileForm()
    user: Users = Users.query.filter_by(id=current_user.id).first()
    profile: Patients = Patients.query.filter_by(p_id=current_user.id).first()

    if form.validate_on_submit():
        avatar = ""
        if form.avatar.data:
            if profile.avatar == "user_male.svg" or profile.avatar == "user_female.svg":
                # Store the new picture in the file system
                avatar = profile_picture_saver(form.avatar.data, "patient")
            else:
                # Remove old picture
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


@patient.route("/dashboard/change_password", methods=["GET", "POST"])
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
            return redirect(url_for("patient.change_password"))

    return render_template(
        "patient/change_password.html", form=form, title="Change Password"
    )


@patient.route("/dashboard/medical_records", methods=["GET", "POST"])
@login_required
def medical_records():
    page_num = request.args.get("page", 1, int)
    form = MedicalInfoForm()
    upload_form = Record_Upload_Form()

    records: Medical_Info = Medical_Info.query.filter_by(
        patient_id=current_user.id
    ).first()
    files: Patient_Record_Files = (
        Patient_Record_Files.query.filter_by(record_patient_id=current_user.id)
        .order_by(Patient_Record_Files.file_id.desc())
        .paginate(page=page_num, per_page=6)
    )

    # Information form handler
    if request.method == "POST":
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
        "patient/medical_records.html",
        form=form,
        upload_form=upload_form,
        files=files,
        title="Medical Records",
    )


# Record file upload handler
@patient.route("/dashboard/upload_record", methods=["POST"])
@login_required
def upload_record():
    upload_form = Record_Upload_Form()

    # File upload form handler
    if upload_form.validate_on_submit() and request.method == "POST":
        file_name = upload_form.file_name.data
        file = upload_form.file.data

        date, time = get_datetime()
        _, file_extension = os.path.splitext(file.filename)
        random_hex = secrets.token_hex(20)
        file_path_name = random_hex + file_extension

        file_path = os.path.join(
            current_app.root_path, "static/upload/patient/records/", file_path_name
        )
        file.save(file_path)
        file_size_kb = float(format(os.path.getsize(file_path) / 1024, ".2f"))

        # Add information to database
        new_file = Patient_Record_Files(
            current_user.id, file_name, file_path_name, file_size_kb, date, time
        )
        new_log = User_Logs(current_user.id, "Upload Medical Record", date, time)
        new_log.log_desc = f"{file_name} ({file_size_kb} KB), file: {file_path_name}"

        db.session.add(new_file)
        db.session.add(new_log)
        db.session.commit()

        flash("File Uploaded Successfully!", category="success")
        return redirect(url_for("patient.medical_records"))
    else:
        flash("Please select correct format!", category="danger")
        return redirect(url_for("patient.medical_records"))


@patient.route("/dashboard/delete_record/<id>", methods=["GET"])
@login_required
def delete_record_file(id):
    file: Patient_Record_Files = Patient_Record_Files.query.filter_by(
        file_id=int(id)
    ).first_or_404()

    if file.record_patient_id == current_user.id:
        date, time = get_datetime()
        new_log = User_Logs(current_user.id, "Delete Medical Record", date, time)
        new_log.log_desc = (
            f"{file.file_name}({file.file_size_kb} KB), {file.file_path_name}"
        )

        os.remove(
            os.path.join(
                current_app.root_path,
                "static/upload/patient/records/",
                file.file_path_name,
            )
        )

        db.session.delete(file)
        db.session.add(new_log)
        db.session.commit()

        flash("File deleted successfully!", category="info")
        return redirect(url_for("patient.medical_records"))
    else:
        flash("Delete failed! Access denied.", category="danger")
        return redirect(url_for("patient.medical_records"))


@patient.route("/dashboard/file/<id>")
@login_required
def view_record_file(id):
    file: Patient_Record_Files = Patient_Record_Files.query.filter_by(
        file_id=int(id)
    ).first_or_404()

    if file.record_patient_id == current_user.id:
        return render_template(
            "patient/record_file_view.html", title=file.file_name, file=file
        )


@patient.route("/download/file/record/<file_id>")
@login_required
def download_record_file(file_id):
    file: Patient_Record_Files = Patient_Record_Files.query.filter_by(
        file_id=int(file_id)
    ).first_or_404()

    if file.record_patient_id == current_user.id:
        file_name = f"{file.file_name}_{file.file_path_name}"
        return send_file(
            os.path.join(
                current_app.root_path,
                "static/upload/patient/records/",
                file.file_path_name,
            ),
            download_name=file_name,
            as_attachment=True,
        )
    else:
        flash("Download failed! Access denied.", category="danger")
        return redirect(url_for("patient.medical_records"))


@patient.route("/dashboard/logs")
@login_required
def logs():
    page_num = request.args.get("page", 1, int)
    logs = (
        User_Logs.query.filter_by(user_id=current_user.id)
        .order_by(User_Logs.log_id.desc())
        .paginate(page=page_num, per_page=12)
    )

    return render_template("patient/logs.html", logs=logs, title="Activity Logs")


@patient.route("/dashboard/invoices")
@login_required
def invoices():
    page_num = request.args.get("page", 1, int)

    invoices = (
        Invoices.query.filter_by(invoice_patient_id=current_user.id)
        .order_by(Invoices.invoice_id.desc())
        .paginate(page=page_num, per_page=12)
    )

    return render_template("patient/invoices.html", title="Invoices", invoices=invoices)


@patient.route("/dashboard/tests")
@login_required
def tests():
    page_num = request.args.get("page", 1, int)

    items = (
        Medical_Test_Book.query.filter(
            Medical_Test_Book.test_patient_id == current_user.id
        )
        .join(
            Invoice_Items,
            Invoice_Items.item_id == Medical_Test_Book.invoice_item_id,
        )
        .join(Invoices, Invoice_Items.invoice_id == Invoices.invoice_id)
        .add_columns(
            Medical_Test_Book.serial_number,
            Medical_Test_Book.invoice_item_id,
            Medical_Test_Book.test_status,
            Invoice_Items.invoice_id,
            Invoice_Items.item_desc,
            Invoice_Items.item_price,
            Invoices.status,
        )
        .paginate(page=page_num, per_page=12)
    )
    return render_template("patient/tests.html", items=items, title="My Medical Tests")


@patient.route("/dashboard/tests/<serial>")
@login_required
def test_report(serial):
    item = (
        Medical_Test_Book.query.filter(Medical_Test_Book.serial_number == serial)
        .join(Invoice_Items, Medical_Test_Book.invoice_item_id == Invoice_Items.item_id)
        .join(Invoices, Invoice_Items.invoice_id == Invoices.invoice_id)
        .join(Medical_Tests, Invoice_Items.test_id_ref == Medical_Tests.test_id)
        .add_columns(
            Medical_Test_Book.serial_number,
            Medical_Test_Book.test_status,
            Invoice_Items.invoice_id,
            Invoice_Items.item_desc,
            Invoice_Items.item_price,
            Invoices.status,
            Invoices.invoice_date,
            Invoices.invoice_time,
            Invoices.invoice_patient_id,
            Medical_Tests.test_desc,
        )
        .first_or_404()
    )

    if item.invoice_patient_id != current_user.id:
        abort(403)

    files = Medical_Report_Files.query.filter(
        Medical_Report_Files.test_book_serial == serial
    ).all()

    return render_template(
        "patient/test_report.html",
        item=item,
        files=files,
        title=f"Report: {item.item_desc}",
    )


@patient.route("/dashboard/tests/<serial_number>/report/<id>")
@login_required
def view_report_file(serial_number, id):
    file = (
        Medical_Report_Files.query.filter(Medical_Report_Files.file_id == int(id))
        .join(
            Medical_Test_Book,
            Medical_Report_Files.test_book_serial == Medical_Test_Book.serial_number,
        )
        .join(Managers, Medical_Report_Files.upload_manager_id == Managers.m_id)
        .add_columns(
            Medical_Report_Files.file_id,
            Medical_Report_Files.file_name,
            Medical_Report_Files.file_path_name,
            Medical_Report_Files.file_size_kb,
            Medical_Report_Files.upload_date,
            Medical_Report_Files.upload_time,
            Medical_Report_Files.test_book_serial,
            Medical_Test_Book.test_patient_id,
            Managers.first_name,
            Managers.last_name,
        )
        .first_or_404()
    )

    if file.test_patient_id != current_user.id:
        abort(403)

    return render_template(
        "patient/report_file_view.html", title=file.file_name, file=file
    )


@patient.route("/download/file/report/<file_id>")
@login_required
def download_report_file(file_id):
    file = (
        Medical_Report_Files.query.filter(Medical_Report_Files.file_id == int(file_id))
        .join(
            Medical_Test_Book,
            Medical_Report_Files.test_book_serial == Medical_Test_Book.serial_number,
        )
        .add_columns(
            Medical_Test_Book.test_patient_id,
            Medical_Report_Files.file_name,
            Medical_Report_Files.file_path_name,
        )
        .first_or_404()
    )

    if file.test_patient_id == current_user.id:
        file_name = f"{file.file_name}_{file.file_path_name}"
        return send_file(
            os.path.join(
                current_app.root_path,
                "static/upload/manager/test_results/",
                file.file_path_name,
            ),
            download_name=file_name,
            as_attachment=True,
        )
    else:
        flash("Download failed! Access denied.", category="danger")
        return redirect(url_for("patient.medical_records"))


@patient.route("/dashboard/appointments")
@login_required
def appointments():
    page_num = request.args.get("page", 1, int)

    appointments = (
        Appointments.query.filter(Appointments.appt_patient_id == current_user.id)
        .join(Appointment_Details, Appointment_Details.appt_id == Appointments.appt_id)
        .join(Doctors, Appointments.appt_doctor_id == Doctors.d_id)
        .join(Users, Users.id == Doctors.d_id)
        .order_by(Appointment_Details.appt_date.desc())
        .add_columns(
            Appointments.appt_id,
            Appointment_Details.appt_status,
            Appointment_Details.appt_date,
            Appointment_Details.appt_time,
            Doctors.d_id,
            Doctors.last_name,
            Doctors.first_name,
            Doctors.title,
            Doctors.avatar,
            Users.gender,
        )
        .paginate(page=page_num, per_page=10)
    )
    return render_template(
        "patient/appointments.html",
        appointments=appointments,
        title=f"Appointment History",
    )


@patient.route("/dashboard/prescriptions")
@login_required
def prescriptions():
    page_num = request.args.get("page", 1, int)

    prescriptions = (
        Prescriptions.query.join(
            Appointments, Appointments.appt_id == Prescriptions.pres_appt_id
        )
        .filter(Appointments.appt_patient_id == current_user.id)
        .join(Appointment_Details, Appointment_Details.appt_id == Appointments.appt_id)
        .join(Doctors, Doctors.d_id == Appointments.appt_doctor_id)
        .join(Users, Users.id == Doctors.d_id)
        .add_columns(
            Prescriptions.prescription_id,
            Prescriptions.last_update_date,
            Appointment_Details.appt_date,
            Appointment_Details.appt_time,
            Doctors.d_id,
            Doctors.last_name,
            Doctors.first_name,
            Users.gender,
        )
        .paginate(page=page_num, per_page=12)
    )

    return render_template(
        "patient/prescriptions.html",
        prescriptions=prescriptions,
        title=f"My Prescriptions",
    )


@patient.route("/dashboard/appointments/<appt_id>/prescription")
@login_required
def view_prescription(appt_id):
    prescription: Prescriptions = Prescriptions.query.filter(
        Prescriptions.pres_appt_id == int(appt_id)
    ).first_or_404()

    return redirect(
        url_for("public.prescription", pres_id=prescription.prescription_id)
    )
