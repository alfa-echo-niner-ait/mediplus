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
    send_from_directory,
)
from flask_login import login_required, current_user
from src.users.models import Users, Patients, User_Logs
from src.patient.models import (
    Medical_Info,
    Patient_Record_Files,
    Invoices,
    Invoice_Items,
    Payments,
    Pending_Items,
)
from src.patient.forms import (
    ChangePasswordForm,
    UpdateProfileForm,
    MedicalInfoForm,
    Record_Upload_Form,
)
from src import db, hash_manager
from src.public.utils import (
    get_datetime,
    profile_picture_saver,
    profile_picture_remover,
)


patient = Blueprint("patient", __name__)

@patient.route("/add_to_cart", methods=["POST"])
@login_required
def add_item_to_cart():
    item_name = request.form.get("item_name")
    item_price = float(request.form.get("item_price"))
    
    item = Pending_Items(current_user.id, item_name, item_price)
    db.session.add(item)
    date, time = get_datetime()
    new_log = User_Logs(current_user.id, "Add Item to Cart", date, time)
    db.session.add(new_log)
    # Commit to the database
    db.session.commit()
    return "success"



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
    ip = request.remote_addr
    info = request.headers.get("User-Agent")

    return render_template(
        "patient/dashboard.html", user=user, ip=ip, info=info, title="Dashboard"
    )


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
        "patient/medical_records.html",
        form=form,
        upload_form=upload_form,
        files=files,
        title="Medical Records",
    )


# Record file upload handler
@patient.route("/dashboard/patient/upload_record", methods=["POST"])
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
        new_log.log_desc = (
            f"{file_name} ({file_size_kb} KB), file: {file_path_name}"
        )

        db.session.add(new_file)
        db.session.add(new_log)
        db.session.commit()

        flash("File Uploaded Successfully!", category="success")
        return redirect(url_for("patient.medical_records"))
    else:
        flash("Please select correct format!", category="danger")
        return redirect(url_for("patient.medical_records"))


@patient.route("/dashboard/patient/delete_record/<id>", methods=["GET"])
@login_required
def delete_record(id):
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


@patient.route("/dashboard/patient/file/<id>")
@login_required
def view_file(id):
    file: Patient_Record_Files = Patient_Record_Files.query.filter_by(
        file_id=int(id)
    ).first_or_404()

    if file.record_patient_id == current_user.id:
        return render_template(
            "patient/file_view.html", title=file.file_name, file=file
        )


@patient.route("/download/file/<file_id>")
@login_required
def download_file(file_id):
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


@patient.route("/dashboard/patient/logs")
@login_required
def logs():
    page_num = request.args.get("page", 1, int)
    logs = (
        User_Logs.query.filter_by(user_id=current_user.id)
        .order_by(User_Logs.log_id.desc())
        .paginate(page=page_num, per_page=10)
    )

    return render_template("patient/logs.html", logs=logs, title="Activity Logs")


@patient.route("/dashboard/patient/invoices")
@login_required
def invoices():
    page_num = request.args.get("page", 1, int)

    invoices = (
        Invoices.query.filter_by(invoice_patient_id=current_user.id)
        .order_by(Invoices.invoice_id.desc())
        .paginate(page=page_num, per_page=12)
    )

    return render_template(
        "patient/invoices.html", title="Invoices", invoices=invoices
    )
