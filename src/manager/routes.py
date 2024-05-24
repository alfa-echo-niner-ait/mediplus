import os
import json
import secrets
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    session,
    abort,
    current_app,
    send_file,
)
from flask_login import login_required, current_user
from sqlalchemy.orm import aliased
from src.users.models import Users, User_Logs, Patients, Doctors, Managers
from src.doctor.models import (
    Doctor_Time,
    Appointments,
    Appointment_Details,
)
from src.patient.models import (
    Invoices,
    Invoice_Items,
    Payments,
    Medical_Info,
    Medical_Tests,
    Medical_Test_Book,
    Medical_Report_Files,
    Patient_Record_Files,
)
from src.doctor.forms import UpdateScheduleForm
from src.manager.forms import (
    LogSortForm,
    ChangePasswordForm,
    SelfProfileForm,
    NewMedicalTestForm,
    UpdateMedicalTestForm,
    UpdateInvoiceForm,
    Test_Result_Upload_Form,
    RegisterDoctorForm,
    UpdateDoctorForm,
    DoctorPasswordForm,
    ManagerPasswordForm,
    RegisterManagerForm,
    SearchInvoiceForm,
    SearchTestbookForm,
    SearchAppointmentForm,
)
from src.public.forms import SearchTestForm, SearchDoctorForm
from src import db, hash_manager
from src.public.utils import (
    get_datetime,
    profile_picture_saver,
    profile_picture_remover,
)
from src.manager.utils import users_pie_data, user_logs_bar_data


# Declare Blueprint
manager = Blueprint("manager", __name__)


@manager.route("/dashboard/manager")
@login_required
def dashboard():
    if current_user.role != "Manager":
        abort(403)

    counts = {
        "patients": Users.query.filter(Users.role == "Patient").count(),
        "managers": Users.query.filter(Users.role == "Manager").count(),
        "doctors": Users.query.filter(Users.role == "Doctor").count(),
        "tests": Medical_Test_Book.query.filter(
            Medical_Test_Book.test_status == "Done"
        ).count(),
        "appt": Appointment_Details.query.filter(
            Appointment_Details.appt_status == "Completed"
        ).count(),
        "invoices": Invoices.query.count(),
    }

    pie_data = users_pie_data()
    bar_data = user_logs_bar_data(days=7)

    return render_template(
        "manager/dashboard.html",
        counts=counts,
        pie_data=json.dumps(pie_data),
        bar_data=json.dumps(bar_data),
        title="Manager Dashboard",
    )


@manager.route("/dashboard/manager/appointments", methods=["GET", "POST"])
@login_required
def appointments():
    if current_user.role != "Manager":
        abort(403)

    page_num = request.args.get("page", 1, int)
    title = "Appointments List"
    search = "no"

    form = SearchAppointmentForm()

    doctors = aliased(Doctors)
    patients = aliased(Patients)

    appointments = (
        Appointments.query.join(
            Appointment_Details, Appointments.appt_id == Appointment_Details.appt_id
        )
        .join(doctors, Appointments.appt_doctor_id == doctors.d_id)
        .join(patients, Appointments.appt_patient_id == patients.p_id)
        .order_by(Appointments.appt_id.desc())
        .add_columns(
            Appointments.appt_id,
            Appointment_Details.appt_status,
            Appointment_Details.appt_date,
            Appointment_Details.appt_time,
            doctors.d_id.label("doctor_id"),
            doctors.last_name.label("doctor_last_name"),
            doctors.first_name.label("doctor_first_name"),
            patients.p_id.label("patient_id"),
            patients.last_name.label("patient_last_name"),
            patients.first_name.label("patient_first_name"),
        )
        .paginate(page=page_num, per_page=15)
    )

    if form.validate_on_submit():
        if page_num > 1:
            page_num = 1
        search = "yes"
        title = f"Search Result: {form.keyword.data}"

        if form.search_by.data == "patient_name":
            appointments = (
                Appointments.query.join(
                    Appointment_Details,
                    Appointments.appt_id == Appointment_Details.appt_id,
                )
                .join(doctors, Appointments.appt_doctor_id == doctors.d_id)
                .join(patients, Appointments.appt_patient_id == patients.p_id)
                .filter(
                    patients.last_name.icontains(form.keyword.data)
                    | patients.first_name.icontains(form.keyword.data)
                )
                .order_by(Appointments.appt_id.desc())
                .add_columns(
                    Appointments.appt_id,
                    Appointment_Details.appt_status,
                    Appointment_Details.appt_date,
                    Appointment_Details.appt_time,
                    doctors.d_id.label("doctor_id"),
                    doctors.last_name.label("doctor_last_name"),
                    doctors.first_name.label("doctor_first_name"),
                    patients.p_id.label("patient_id"),
                    patients.last_name.label("patient_last_name"),
                    patients.first_name.label("patient_first_name"),
                )
                .paginate(page=page_num, per_page=15)
            )
        elif form.search_by.data == "doctor_name":
            appointments = (
                Appointments.query.join(
                    Appointment_Details,
                    Appointments.appt_id == Appointment_Details.appt_id,
                )
                .join(doctors, Appointments.appt_doctor_id == doctors.d_id)
                .join(patients, Appointments.appt_patient_id == patients.p_id)
                .filter(
                    doctors.last_name.icontains(form.keyword.data)
                    | doctors.first_name.icontains(form.keyword.data)
                )
                .order_by(Appointments.appt_id.desc())
                .add_columns(
                    Appointments.appt_id,
                    Appointment_Details.appt_status,
                    Appointment_Details.appt_date,
                    Appointment_Details.appt_time,
                    doctors.d_id.label("doctor_id"),
                    doctors.last_name.label("doctor_last_name"),
                    doctors.first_name.label("doctor_first_name"),
                    patients.p_id.label("patient_id"),
                    patients.last_name.label("patient_last_name"),
                    patients.first_name.label("patient_first_name"),
                )
                .paginate(page=page_num, per_page=15)
            )
        elif form.search_by.data == "date":
            appointments = (
                Appointments.query.join(
                    Appointment_Details,
                    Appointments.appt_id == Appointment_Details.appt_id,
                )
                .join(doctors, Appointments.appt_doctor_id == doctors.d_id)
                .join(patients, Appointments.appt_patient_id == patients.p_id)
                .filter(Appointment_Details.appt_date == form.keyword.data)
                .order_by(Appointments.appt_id.desc())
                .add_columns(
                    Appointments.appt_id,
                    Appointment_Details.appt_status,
                    Appointment_Details.appt_date,
                    Appointment_Details.appt_time,
                    doctors.d_id.label("doctor_id"),
                    doctors.last_name.label("doctor_last_name"),
                    doctors.first_name.label("doctor_first_name"),
                    patients.p_id.label("patient_id"),
                    patients.last_name.label("patient_last_name"),
                    patients.first_name.label("patient_first_name"),
                )
                .paginate(page=page_num, per_page=15)
            )

    return render_template(
        "manager/appointments.html",
        appointments=appointments,
        form=form,
        search=search,
        title=title,
    )


@manager.route("/dashboard/manager/appointments/<appt_id>/cancel")
@login_required
def cancel_appointment(appt_id):
    if current_user.role != "Manager":
        abort(403)

    appointment_details: Appointment_Details = Appointment_Details.query.filter(
        Appointment_Details.appt_id == int(appt_id)
    ).first_or_404()
    appointment_details.appt_status = "Cancelled"
    appointment: Appointments = Appointments.query.filter(
        Appointments.appt_id == int(appt_id)
    ).first()

    date, time = get_datetime()
    manager_log: User_Logs = User_Logs(
        current_user.id, "Cancel Appointment", date, time
    )
    manager_log.log_desc = f"Appointment #{appointment.appt_id}, Patient #{appointment.appt_patient_id} on {appointment_details.appt_date} ({appointment_details.appt_time})"
    db.session.add(manager_log)

    patient_log: User_Logs = User_Logs(
        appointment.appt_patient_id, "Appointment Cancelled", date, time
    )
    patient_log.log_desc = (
        f"Doctor has cancelled your appointment. Try different date/time slot."
    )
    db.session.add(patient_log)

    db.session.commit()

    flash("Appointment has been cancelled!", category="warning")
    return redirect(url_for("manager.appointments"))


@manager.route("/dashboard/manager/tests", methods=["GET", "POST"])
@login_required
def tests():
    if current_user.role != "Manager":
        abort(403)

    page_num = request.args.get("page", 1, int)
    title = "Medical Tests Booking"
    search = "no"

    form = SearchTestbookForm()

    items = (
        Medical_Test_Book.query.join(
            Invoice_Items,
            Invoice_Items.item_id == Medical_Test_Book.invoice_item_id,
        )
        .order_by(Medical_Test_Book.serial_number.desc())
        .join(Invoices, Invoice_Items.invoice_id == Invoices.invoice_id)
        .join(Patients, Patients.p_id == Invoices.invoice_patient_id)
        .join(Users, Users.id == Patients.p_id)
        .add_columns(
            Medical_Test_Book.serial_number,
            Medical_Test_Book.invoice_item_id,
            Medical_Test_Book.test_status,
            Invoice_Items.invoice_id,
            Invoice_Items.item_desc,
            Invoices.status,
            Invoices.invoice_date,
            Users.gender,
            Patients.p_id,
            Patients.last_name,
            Patients.first_name,
        )
        .paginate(page=page_num, per_page=15)
    )

    if form.validate_on_submit():
        if page_num > 1:
            page_num = 1
        search = "yes"
        title = f"Test Search: {form.keyword.data}"
        if form.search_by.data == "serial":
            items = (
                Medical_Test_Book.query.filter(
                    Medical_Test_Book.serial_number == int(form.keyword.data)
                )
                .join(
                    Invoice_Items,
                    Invoice_Items.item_id == Medical_Test_Book.invoice_item_id,
                )
                .order_by(Medical_Test_Book.serial_number.desc())
                .join(Invoices, Invoice_Items.invoice_id == Invoices.invoice_id)
                .join(Patients, Patients.p_id == Invoices.invoice_patient_id)
                .join(Users, Users.id == Patients.p_id)
                .add_columns(
                    Medical_Test_Book.serial_number,
                    Medical_Test_Book.invoice_item_id,
                    Medical_Test_Book.test_status,
                    Invoice_Items.invoice_id,
                    Invoice_Items.item_desc,
                    Invoices.status,
                    Invoices.invoice_date,
                    Users.gender,
                    Patients.p_id,
                    Patients.last_name,
                    Patients.first_name,
                )
                .paginate(page=page_num, per_page=15)
            )
        elif form.search_by.data == "patient_name":
            items = (
                Medical_Test_Book.query.join(
                    Invoice_Items,
                    Invoice_Items.item_id == Medical_Test_Book.invoice_item_id,
                )
                .join(Invoices, Invoice_Items.invoice_id == Invoices.invoice_id)
                .join(Patients, Patients.p_id == Invoices.invoice_patient_id)
                .filter(
                    Patients.last_name.icontains(form.keyword.data)
                    | Patients.first_name.icontains(form.keyword.data)
                )
                .join(Users, Users.id == Patients.p_id)
                .order_by(Medical_Test_Book.serial_number.desc())
                .add_columns(
                    Medical_Test_Book.serial_number,
                    Medical_Test_Book.invoice_item_id,
                    Medical_Test_Book.test_status,
                    Invoice_Items.invoice_id,
                    Invoice_Items.item_desc,
                    Invoices.status,
                    Invoices.invoice_date,
                    Users.gender,
                    Patients.p_id,
                    Patients.last_name,
                    Patients.first_name,
                )
                .paginate(page=page_num, per_page=15)
            )
        elif form.search_by.data == "date":
            items = (
                Medical_Test_Book.query.join(
                    Invoice_Items,
                    Invoice_Items.item_id == Medical_Test_Book.invoice_item_id,
                )
                .join(Invoices, Invoice_Items.invoice_id == Invoices.invoice_id)
                .filter(Invoices.invoice_date == form.keyword.data)
                .join(Patients, Patients.p_id == Invoices.invoice_patient_id)
                .join(Users, Users.id == Patients.p_id)
                .order_by(Medical_Test_Book.serial_number.desc())
                .add_columns(
                    Medical_Test_Book.serial_number,
                    Medical_Test_Book.invoice_item_id,
                    Medical_Test_Book.test_status,
                    Invoice_Items.invoice_id,
                    Invoice_Items.item_desc,
                    Invoices.status,
                    Invoices.invoice_date,
                    Users.gender,
                    Patients.p_id,
                    Patients.last_name,
                    Patients.first_name,
                )
                .paginate(page=page_num, per_page=15)
            )

    return render_template(
        "manager/tests.html",
        form=form,
        items=items,
        search=search,
        title=title,
    )


@manager.route("/dashboard/manager/tests/<serial_number>", methods=["GET", "POST"])
@login_required
def test_details(serial_number):
    if current_user.role != "Manager":
        abort(403)

    upload_form = Test_Result_Upload_Form()

    item = (
        Medical_Test_Book.query.filter(Medical_Test_Book.serial_number == serial_number)
        .join(Invoice_Items, Medical_Test_Book.invoice_item_id == Invoice_Items.item_id)
        .join(Invoices, Invoice_Items.invoice_id == Invoices.invoice_id)
        .join(Medical_Tests, Invoice_Items.test_id_ref == Medical_Tests.test_id)
        .join(Patients, Medical_Test_Book.test_patient_id == Patients.p_id)
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
            Patients.p_id,
            Patients.first_name,
            Patients.last_name,
            Patients.phone,
        )
        .first_or_404()
    )

    files = (
        Medical_Report_Files.query.filter(
            Medical_Report_Files.test_book_serial == serial_number
        )
        .join(Managers, Medical_Report_Files.upload_manager_id == Managers.m_id)
        .add_columns(
            Medical_Report_Files.file_id,
            Medical_Report_Files.file_name,
            Medical_Report_Files.file_size_kb,
            Medical_Report_Files.upload_date,
            Medical_Report_Files.upload_time,
            Managers.m_id,
            Managers.first_name,
            Managers.last_name,
        )
        .all()
    )

    return render_template(
        "manager/test_report_details.html",
        item=item,
        files=files,
        upload_form=upload_form,
        title=f"Test: {item.test_desc}",
    )


# Mark test as completed
@manager.route("/dashboard/manager/tests/<serial_number>/done")
@login_required
def test_mark_as_done(serial_number):
    if current_user.role != "Manager":
        abort(403)

    item: Medical_Test_Book = Medical_Test_Book.query.filter(
        Medical_Test_Book.serial_number == serial_number
    ).first_or_404()
    item.test_status = "Done"

    date, time = get_datetime()
    new_log = User_Logs(current_user.id, "Mark Test Done", date, time)
    new_log.log_desc = f"Test Book Serial #{serial_number}, Invoice Item #{item.invoice_item_id}, Patient #{item.test_patient_id}"

    db.session.add(new_log)
    db.session.commit()

    flash("Test Status Changed Successfully!", category="success")
    return redirect(url_for("manager.test_details", serial_number=serial_number))


# Record file upload handler
@manager.route("/dashboard/manager/tests/<serial_number>/upload", methods=["POST"])
@login_required
def upload_test_report(serial_number):
    if current_user.role != "Manager":
        abort(403)

    upload_form = Test_Result_Upload_Form()

    # File upload form handler
    if upload_form.validate_on_submit() and request.method == "POST":
        file_name = upload_form.file_name.data
        file = upload_form.file.data

        date, time = get_datetime()
        _, file_extension = os.path.splitext(file.filename)
        random_hex = secrets.token_hex(20)
        file_path_name = random_hex + file_extension

        file_path = os.path.join(
            current_app.root_path, "static/upload/manager/test_results/", file_path_name
        )
        file.save(file_path)
        file_size_kb = float(format(os.path.getsize(file_path) / 1024, ".2f"))

        # Add information to database
        new_file = Medical_Report_Files(
            serial_number,
            file_name,
            file_path_name,
            file_size_kb,
            current_user.id,
            date,
            time,
        )
        new_log = User_Logs(current_user.id, "Upload Test Result", date, time)
        new_log.log_desc = f"Test Book Serial #{serial_number}, {file_name} ({file_size_kb} KB), file: {file_path_name}"

        db.session.add(new_file)
        db.session.add(new_log)
        db.session.commit()

        flash("File Uploaded Successfully!", category="success")
        return redirect(url_for("manager.test_details", serial_number=serial_number))
    else:
        flash("Please select correct file format!", category="danger")
        return redirect(url_for("manager.test_details", serial_number=serial_number))


@manager.route("/dashboard/manager/download/test_report/<file_id>")
@login_required
def download_test_report(file_id):
    if current_user.role != "Manager":
        abort(403)

    file = Medical_Report_Files.query.filter(
        Medical_Report_Files.file_id == int(file_id)
    ).first_or_404()

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


@manager.route("/dashboard/manager/tests/<serial_number>/report/<file_id>")
@login_required
def view_test_report(serial_number, file_id):
    if current_user.role != "Manager":
        abort(403)

    file = (
        Medical_Report_Files.query.filter(Medical_Report_Files.file_id == int(file_id))
        .join(
            Medical_Test_Book,
            Medical_Test_Book.serial_number == Medical_Report_Files.test_book_serial,
        )
        .join(Invoice_Items, Medical_Test_Book.invoice_item_id == Invoice_Items.item_id)
        .join(Managers, Managers.m_id == Medical_Report_Files.upload_manager_id)
        .add_columns(
            Medical_Report_Files.file_id,
            Medical_Report_Files.file_name,
            Medical_Report_Files.file_path_name,
            Medical_Report_Files.file_size_kb,
            Medical_Report_Files.upload_date,
            Medical_Report_Files.upload_time,
            Medical_Report_Files.test_book_serial,
            Invoice_Items.item_desc,
            Medical_Test_Book.serial_number,
            Managers.m_id,
            Managers.first_name,
            Managers.last_name,
            Managers.phone,
        )
        .first_or_404()
    )

    return render_template(
        "manager/report_file_view.html", title=file.file_name, file=file
    )


@manager.route("/dashboard/manager/tests/<serial_number>/delete/<file_id>")
@login_required
def delete_test_report(serial_number, file_id):
    if current_user.role != "Manager":
        abort(403)

    file: Medical_Report_Files = Medical_Report_Files.query.filter(
        Medical_Report_Files.file_id == int(file_id)
    ).first_or_404()

    date, time = get_datetime()
    new_log = User_Logs(current_user.id, "Delete Test Report", date, time)
    new_log.log_desc = f"Test #{file.test_book_serial}, Upload Manager #{file.upload_manager_id}: {file.file_name}({file.file_size_kb} KB), {file.file_path_name}"

    # Remove from storage
    os.remove(
        os.path.join(
            current_app.root_path,
            "static/upload/manager/test_results/",
            file.file_path_name,
        )
    )
    # Remove record from database
    db.session.delete(file)
    db.session.add(new_log)
    db.session.commit()

    flash("File deleted successfully!", category="info")
    return redirect(url_for("manager.test_details", serial_number=serial_number))


@manager.route("/dashboard/manager/tests/catalog", methods=["GET", "POST"])
@login_required
def test_catalog():
    if current_user.role != "Manager":
        abort(403)

    new_test_form = NewMedicalTestForm()
    search_form = SearchTestForm()
    title = "Medical Tests"
    search = "no"

    page_num = request.args.get("page", 1, int)
    tests = Medical_Tests.query.order_by(Medical_Tests.test_name.asc()).paginate(
        page=page_num, per_page=15
    )

    if search_form.validate_on_submit():
        if page_num > 1:
            page_num = 1
        tests = Medical_Tests.query.filter(
            Medical_Tests.test_name.icontains(search_form.keyword.data)
            | Medical_Tests.test_desc.icontains(search_form.keyword.data)
        ).paginate(page=page_num, per_page=15)

        title = f"Search Result: {search_form.keyword.data}"
        search = "yes"

    return render_template(
        "manager/test_catalog.html",
        new_test_form=new_test_form,
        search_form=search_form,
        tests=tests,
        search=search,
        title=title,
    )


@manager.route("/dashboard/manager/tests/add", methods=["POST"])
@login_required
def add_new_test():
    if current_user.role != "Manager":
        abort(403)

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
        return redirect(url_for("manager.test_catalog"))
    else:
        flash("Operation failed! Submission error", category="danger")
        return redirect(url_for("manager.test_catalog"))


@manager.route("/dashboard/manager/tests/catalog/<test_id>", methods=["GET", "POST"])
@login_required
def view_test(test_id):
    if current_user.role != "Manager":
        abort(403)

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
    if current_user.role != "Manager":
        abort(403)

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


@manager.route("/dashboard/manager/invoices", methods=["GET", "POST"])
@login_required
def invoices():
    if current_user.role != "Manager":
        abort(403)

    page_num = request.args.get("page", 1, int)
    title = "Invoices Management"
    search = "no"
    form = SearchInvoiceForm()

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
        .paginate(page=page_num, per_page=15)
    )

    if form.validate_on_submit():
        title = f"Invoice Search: {form.keyword.data}"
        search = "yes"

        if page_num > 1:
            page_num = 1

        if form.search_by.data == "invoice_id":
            invoices = (
                Invoices.query.filter(Invoices.invoice_id == int(form.keyword.data))
                .join(Patients, Invoices.invoice_patient_id == Patients.p_id)
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
                .paginate(page=page_num, per_page=15)
            )
        elif form.search_by.data == "patient_name":
            invoices = (
                Invoices.query.join(
                    Patients, Invoices.invoice_patient_id == Patients.p_id
                )
                .filter(
                    Patients.last_name.icontains(form.keyword.data)
                    | Patients.first_name.icontains(form.keyword.data)
                )
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
                .paginate(page=page_num, per_page=20)
            )

    return render_template(
        "manager/invoices.html",
        search=search,
        title=title,
        form=form,
        invoices=invoices,
    )


@manager.route("/dashboard/manager/invoices/<id>")
@login_required
def invoice_update(id):
    if current_user.role != "Manager":
        abort(403)

    form = UpdateInvoiceForm()
    invoice: Invoices = Invoices.query.filter_by(invoice_id=id).first_or_404()
    items: Invoice_Items = Invoice_Items.query.filter_by(invoice_id=id).all()
    patient: Patients = Patients.query.filter_by(
        p_id=invoice.invoice_patient_id
    ).first()

    if request.method == "GET":
        form.payment_amount.data = invoice.total_amount

    return render_template(
        "manager/invoice_update.html",
        invoice=invoice,
        items=items,
        patient=patient,
        form=form,
        title=f"Invoice #{invoice.invoice_id}",
    )


@manager.route("/dashboard/manager/invoices/delete/<id>")
@login_required
def invoice_delete(id):
    if current_user.role != "Manager":
        abort(403)

    invoice: Invoices = Invoices.query.filter_by(invoice_id=id).first_or_404()
    db.session.delete(invoice)

    date, time = get_datetime()
    new_log_manager: User_Logs = User_Logs(
        current_user.id, "Delete Invoice", date, time
    )
    new_log_manager.log_desc = f"Invoice #{invoice.invoice_id}, Total Amount: {invoice.total_amount} ({invoice.status})"
    db.session.add(new_log_manager)
    new_log_patient: User_Logs = User_Logs(
        invoice.invoice_patient_id, "*Invoice Deleted", date, time
    )
    new_log_patient.log_desc = f"Invoice #{invoice.invoice_id} Deleted by Manager, Total Amount: {invoice.total_amount} ({invoice.status})"
    db.session.add(new_log_patient)
    # Commit to the database
    db.session.commit()

    flash("Invoice deleted successfully!", category="info")
    return redirect(url_for("manager.invoices"))


# Receive Payment for Invoice
@manager.route("/dashboard/manager/invoices/<invoice_id>/update", methods=["POST"])
@login_required
def invoice_payment_update(invoice_id):
    if current_user.role != "Manager":
        abort(403)

    form = UpdateInvoiceForm()
    invoice: Invoices = Invoices.query.filter_by(invoice_id=invoice_id).first_or_404()
    date, time = get_datetime()

    payment = Payments(
        invoice.invoice_id, current_user.id, form.payment_amount.data, date, time
    )
    payment.payment_method = form.payment_method.data
    payment.payment_note = form.payment_note.data
    db.session.add(payment)
    invoice.status = "Paid"
    db.session.commit()

    new_log_manager = User_Logs(current_user.id, "Receive Payment", date, time)
    new_log_manager.log_desc = f"Payment #{payment.payment_id}, Invoice #{invoice.invoice_id}, Amount: {form.payment_amount.data} ({form.payment_method.data})"
    db.session.add(new_log_manager)

    new_log_patient = User_Logs(invoice.invoice_patient_id, "Invoice Paid", date, time)
    new_log_patient.log_desc = f"Payment #{payment.payment_id}, Invoice #{invoice.invoice_id}, Amount: {form.payment_amount.data} ({form.payment_method.data})"
    db.session.add(new_log_patient)
    # Commit to the database
    db.session.commit()

    flash("Invoice updated successfully!", category="success")
    return redirect(url_for("manager.invoice_update", id=invoice_id))


@manager.route("/dashboard/manager/invoices/<invoice_id>/delete/<item_id>")
@login_required
def invoice_item_delete(invoice_id, item_id):
    if current_user.role != "Manager":
        abort(403)

    item: Invoice_Items = Invoice_Items.query.filter_by(item_id=item_id).first_or_404()
    db.session.delete(item)

    date, time = get_datetime()
    new_log: User_Logs = User_Logs(current_user.id, "Delete Test", date, time)
    new_log.log_desc = f"#{item.item_id} {item.item_desc} ({item.item_price} RMB) from Invoice #{invoice_id}"
    db.session.add(new_log)
    # Commit to the database
    db.session.commit()

    flash("Item deleted successfully!", category="warning")
    return redirect(url_for("manager.invoice_update", id=invoice_id))


@manager.route("/dashboard/manager/managers")
@login_required
def managers():
    if current_user.role != "Manager":
        abort(403)

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
        )
        .order_by(Managers.m_id.desc())
        .paginate(page=page_num, per_page=12)
    )

    return render_template("manager/managers.html", managers=managers, title="Managers")


@manager.route("/dashboard/manager/managers/<id>")
@login_required
def view_manager(id):
    if current_user.role != "Manager":
        abort(403)

    page_num = request.args.get("page", 1, int)
    password_form = ManagerPasswordForm()

    manager = (
        Managers.query.filter(Managers.m_id == int(id))
        .join(Users, Users.id == Managers.m_id)
        .add_columns(
            Users.id,
            Users.username,
            Users.gender,
            Users.email,
            Users.role,
            Managers.first_name,
            Managers.last_name,
            Managers.phone,
            Managers.birthdate,
            Managers.avatar,
        )
        .first_or_404()
    )
    logs = (
        User_Logs.query.filter_by(user_id=int(id))
        .order_by(User_Logs.log_id.desc())
        .paginate(page=page_num, per_page=15)
    )

    return render_template(
        "manager/view_manager.html",
        password_form=password_form,
        manager=manager,
        logs=logs,
        title=f"Manager {manager.last_name} {manager.first_name}",
    )


@manager.route("/dashboard/manager/managers/register", methods=["GET", "POST"])
@login_required
def register_manager():
    if current_user.role != "Manager":
        abort(403)

    form = RegisterManagerForm()

    if form.validate_on_submit():
        # Account Info
        username = form.username.data
        password = form.password.data
        email = form.email.data
        phone = form.phone.data

        password_hash = hash_manager.generate_password_hash(password).decode("utf-8")
        # Manager Info
        first_name = form.first_name.data
        last_name = form.last_name.data
        gender = form.gender.data
        birthday = form.birthdate.data
        avatar = "manager.svg"

        # Create New User
        new_user = Users(username, password_hash, email, gender, "Manager")
        db.session.add(new_user)
        db.session.commit()

        # Create New Manager
        new_manager = Managers(
            new_user.id, first_name, last_name, phone, birthday, avatar
        )
        db.session.add(new_manager)
        db.session.commit()

        # Create Log
        date, time = get_datetime()
        # New Manager Log
        new_log = User_Logs(new_manager.m_id, "Account Registration", date, time)
        new_log.log_desc = f"Account Registered by Manager #{current_user.id} ({current_user.username})"
        db.session.add(new_log)
        # Register Manager Log
        new_log = User_Logs(current_user.id, "Add New Manager", date, time)
        new_log.log_desc = f"Registered New Manager #{new_manager.m_id} ({username})"
        db.session.add(new_log)

        db.session.commit()

        flash("New Manager Registered Successfully!", category="success")
        return redirect(url_for("manager.managers"))

    return render_template(
        "manager/register_manager.html", form=form, title="Register New Manager"
    )


@manager.route("/dashboard/manager/managers/<id>/delete")
@login_required
def delete_manager(id):
    if current_user.role != "Manager":
        abort(403)

    user: Users = Users.query.filter(Users.id == int(id)).first_or_404()
    manager: Managers = Managers.query.filter(Managers.m_id == int(id)).first_or_404()
    db.session.delete(user)

    date, time = get_datetime()
    # Manager Log
    new_log = User_Logs(current_user.id, "Delete Manager Account", date, time)
    new_log.log_desc = (
        f"Manager #{id}({user.username}),{manager.last_name} {manager.first_name}"
    )
    db.session.add(new_log)
    db.session.commit()

    flash("Manager Account Deleted Successfully!", category="warning")
    return redirect(url_for("manager.managers"))


@manager.route("/dashboard/manager/managers/<id>/update/password", methods=["POST"])
@login_required
def update_manager_password_handler(id):
    if current_user.role != "Manager":
        abort(403)

    password_form = ManagerPasswordForm()
    if password_form.validate_on_submit():
        user: Users = Users.query.filter(Users.id == int(id)).first_or_404()
        
        password_hash = hash_manager.generate_password_hash(
            password_form.new_password.data
        ).decode("utf-8")

        user.password_hash = password_hash

        date, time = get_datetime()
        new_log = User_Logs(current_user.id, "Update Manager Password", date, time)
        new_log.log_desc = f"Manager #{id} @ {user.username}"
        db.session.add(new_log)

        db.session.commit()
        flash("Password Changed Successfully!", category="success")
        return redirect(url_for("manager.view_manager", id=id))

    else:
        flash("Password Change Failed!", category="danger")
        return redirect(url_for("manager.view_manager", id=id))


@manager.route("/dashboard/manager/doctors", methods=["GET", "POST"])
@login_required
def doctors():
    if current_user.role != "Manager":
        abort(403)

    page_num = request.args.get("page", 1, int)
    title = "Doctors"
    search = "no"
    form = SearchDoctorForm()

    doctors = (
        Doctors.query.join(Users, Doctors.d_id == Users.id)
        .join(Doctor_Time, Doctor_Time.doctor_id == Doctors.d_id)
        .add_columns(
            Users.username,
            Users.gender,
            Doctors.d_id,
            Doctors.title,
            Doctors.first_name,
            Doctors.last_name,
            Doctors.phone,
            Doctor_Time.appt_status,
        )
        .paginate(page=page_num, per_page=12)
    )

    if form.validate_on_submit():
        if page_num > 1:
            page_num = 1
        search = "yes"
        title = f"Doctor Search: {form.keyword.data}"

        doctors = (
            Doctors.query.filter(
                Doctors.title.icontains(form.keyword.data)
                | Doctors.last_name.icontains(form.keyword.data)
                | Doctors.first_name.icontains(form.keyword.data)
            )
            .join(Users, Doctors.d_id == Users.id)
            .join(Doctor_Time, Doctor_Time.doctor_id == Doctors.d_id)
            .add_columns(
                Users.username,
                Users.gender,
                Doctors.d_id,
                Doctors.title,
                Doctors.first_name,
                Doctors.last_name,
                Doctors.phone,
                Doctor_Time.appt_status,
            )
            .paginate(page=page_num, per_page=12)
        )

    return render_template(
        "manager/doctors.html", doctors=doctors, form=form, search=search, title=title
    )


@manager.route("/dashboard/manager/doctors/<id>")
@login_required
def view_doctor(id):
    if current_user.role != "Manager":
        abort(403)

    page_num = request.args.get("page", 1, int)
    password_form = DoctorPasswordForm()
    doctor = (
        Doctors.query.filter(Doctors.d_id == int(id))
        .join(Users, Doctors.d_id == Users.id)
        .join(Doctor_Time, Doctors.d_id == Doctor_Time.doctor_id)
        .add_columns(
            Users.username,
            Users.gender,
            Doctors.d_id,
            Doctors.first_name,
            Doctors.last_name,
            Doctors.title,
            Doctors.phone,
            Doctors.avatar,
            Doctor_Time.appt_status,
        )
        .first_or_404()
    )

    appointments = (
        Appointments.query.filter(Appointments.appt_doctor_id == doctor.d_id)
        .join(Appointment_Details, Appointments.appt_id == Appointment_Details.appt_id)
        .join(Patients, Appointments.appt_patient_id == Patients.p_id)
        .join(Users, Patients.p_id == Users.id)
        .order_by(Appointment_Details.appt_date.desc())
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
        .paginate(page=page_num, per_page=10)
    )

    return render_template(
        "manager/doctor_view.html",
        doctor=doctor,
        appointments=appointments,
        password_form=password_form,
        title=f"Dr. {doctor.last_name} {doctor.first_name}",
    )


@manager.route("/dashboard/manager/doctors/<id>/change_status")
@login_required
def change_appt_status(id):
    if current_user.role != "Manager":
        abort(403)

    doctor_time: Doctor_Time = Doctor_Time.query.filter(
        Doctor_Time.doctor_id == int(id)
    ).first_or_404()
    if doctor_time.appt_status == "Available":
        doctor_time.appt_status = "Unavailable"
    else:
        doctor_time.appt_status = "Available"

    date, time = get_datetime()
    new_log = User_Logs(current_user.id, "Change Doctor Status", date, time)
    new_log.log_desc = f"Doctor #{id}"
    db.session.add(new_log)
    db.session.commit()

    flash("Status Changed Successfully!", category="success")
    return redirect(url_for("manager.view_doctor", id=id))


@manager.route(
    "/dashboard/manager/doctors/<id>/update/schedule", methods=["GET", "POST"]
)
@login_required
def update_doctor_schedule(id):
    if current_user.role != "Manager":
        abort(403)

    doctor: Doctors = Doctors.query.filter(Doctors.d_id == int(id)).first()
    doctor_time: Doctor_Time = Doctor_Time.query.filter(
        Doctor_Time.doctor_id == int(id)
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
        new_log = User_Logs(current_user.id, "Update Doctor Schedule", date, time)
        new_log.log_desc = f"Doctor #{id}: Dr. {doctor.last_name} {doctor.first_name}"
        db.session.add(new_log)
        db.session.commit()

        flash("Schedule Updated Successfully!", category="success")
        return redirect(url_for("manager.update_doctor_schedule", id=id))

    elif request.method == "POST":
        flash("Empty field can't be accepted!", category="warning")
        return redirect(url_for("manager.update_doctor_schedule", id=id))

    return render_template(
        "manager/doctor_update_schedule.html",
        form=form,
        doctor=doctor,
        title=f"Update Schedule Dr. {doctor.last_name} {doctor.first_name}",
    )


@manager.route("/dashboard/manager/doctors/<id>/update", methods=["GET"])
@login_required
def update_doctor_profile(id):
    if current_user.role != "Manager":
        abort(403)

    doctor = (
        Doctors.query.filter(Doctors.d_id == int(id))
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

    form = UpdateDoctorForm()
    if request.method == "GET":
        form.title.data = doctor.title
        form.first_name.data = doctor.first_name
        form.last_name.data = doctor.last_name
        form.gender.data = doctor.gender
        form.birthdate.data = doctor.birthdate
        form.phone.data = doctor.phone
        form.email.data = doctor.email

    return render_template(
        "manager/doctor_update_profile.html",
        doctor=doctor,
        form=form,
        title=f"Update Dr. {doctor.last_name} {doctor.first_name}",
    )


@manager.route("/dashboard/manager/doctors/<id>/update/profile", methods=["POST"])
@login_required
def update_doctor_profile_handler(id):
    if current_user.role != "Manager":
        abort(403)

    user: Users = Users.query.filter(Users.id == id).first_or_404()
    doctor: Doctors = Doctors.query.filter(Doctors.d_id == id).first_or_404()

    form = UpdateDoctorForm()
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
        new_log = User_Logs(current_user.id, "Update Doctor Profile", date, time)
        new_log.log_desc = f"Doctor #{id}: Dr. {doctor.last_name} {doctor.first_name}"
        db.session.add(new_log)
        db.session.commit()

        flash("Profile Updated Successfully!", category="success")
        return redirect(url_for("manager.update_doctor_profile", id=id))
    else:
        flash("Profile Update Failed!", category="danger")
        return redirect(url_for("manager.update_doctor_profile", id=id))


@manager.route("/dashboard/manager/doctors/<id>/update/password", methods=["POST"])
@login_required
def update_doctor_password_handler(id):
    if current_user.role != "Manager":
        abort(403)

    password_form = DoctorPasswordForm()
    if password_form.validate_on_submit():
        user: Users = Users.query.filter(Users.id == int(id)).first_or_404()
        if user.role != "Doctor":
            abort(403)

        password_hash = hash_manager.generate_password_hash(
            password_form.new_password.data
        ).decode("utf-8")

        user.password_hash = password_hash

        date, time = get_datetime()
        new_log = User_Logs(current_user.id, "Update Doctor Password", date, time)
        new_log.log_desc = f"Doctor #{id} @ {user.username}"
        db.session.add(new_log)

        db.session.commit()
        flash("Password Changed Successfully!", category="success")
        return redirect(url_for("manager.view_doctor", id=id))

    else:
        flash("Password Change Failed!", category="danger")
        return redirect(url_for("manager.view_doctor", id=id))


@manager.route("/dashboard/manager/doctors/register", methods=["GET", "POST"])
@login_required
def register_doctor():
    if current_user.role != "Manager":
        abort(403)

    form = RegisterDoctorForm()

    if form.validate_on_submit():
        # Account Info
        username = form.username.data
        password = form.password.data
        email = form.email.data
        phone = form.phone.data

        password_hash = hash_manager.generate_password_hash(password).decode("utf-8")
        # Doctor Info
        title = form.title.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        gender = form.gender.data
        birthday = form.birthdate.data
        avatar = ""

        if gender == "Male":
            avatar = "doctor_male.png"
        else:
            avatar = "doctor_female.png"

        # Create New User
        new_user = Users(username, password_hash, email, gender, "Doctor")
        db.session.add(new_user)
        db.session.commit()

        # Create New Doctor
        new_doctor = Doctors(
            new_user.id, first_name, last_name, phone, birthday, title, avatar
        )
        db.session.add(new_doctor)
        db.session.commit()

        # Init new doctor time
        doctor_time = Doctor_Time(new_doctor.d_id)
        db.session.add(doctor_time)
        db.session.commit()

        # Create Log
        date, time = get_datetime()
        # Doctor Log
        new_log = User_Logs(new_doctor.d_id, "Account Registration", date, time)
        new_log.log_desc = f"Registered New Doctor #{new_doctor.d_id} ({username}) by Manager #{current_user.id}"
        db.session.add(new_log)
        # Manager Log
        new_log = User_Logs(current_user.id, "New Doctor Registration", date, time)
        new_log.log_desc = f"Registered New Doctor #{new_doctor.d_id} ({username}) by Manager #{current_user.id}"
        db.session.add(new_log)

        db.session.commit()

        flash("New Doctor Registered Successfully!", category="success")
        return redirect(url_for("manager.doctors"))

    return render_template(
        "manager/register_doctor.html", form=form, title="Register New Doctors"
    )


@manager.route("/dashboard/manager/doctors/<id>/delete")
@login_required
def delete_doctor(id):
    if current_user.role != "Manager":
        abort(403)

    user = Users.query.filter(Users.id == int(id)).first_or_404()
    doctor = Doctors.query.filter(Doctors.d_id == int(id)).first_or_404()
    db.session.delete(user)

    date, time = get_datetime()
    # Manager Log
    new_log = User_Logs(current_user.id, "Delete Doctor Account", date, time)
    new_log.log_desc = f"Doctor #{id}, Dr. {doctor.last_name} {doctor.first_name}"
    db.session.add(new_log)
    db.session.commit()

    flash("Doctor Account Deleted Successfully!", category="warning")
    return redirect(url_for("manager.doctors"))


# Patients
@manager.route("/dashboard/manager/patients")
@login_required
def patients():
    if current_user.role != "Manager":
        abort(403)

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
        )
        .order_by(Patients.p_id.desc())
        .paginate(page=page_num, per_page=15)
    )
    return render_template("manager/patients.html", title="Patients", patients=patients)


@manager.route("/dashboard/manager/patients/<id>")
def view_patient(id):
    if current_user.role != "Manager":
        abort(403)

    page_num = request.args.get("page", 1, int)

    patient: Patients = (
        Patients.query.filter(Patients.p_id == int(id))
        .join(Users, Users.id == Patients.p_id)
        .join(Medical_Info, Medical_Info.patient_id == Patients.p_id)
        .add_columns(
            Patients.p_id,
            Patients.last_name,
            Patients.first_name,
            Patients.phone,
            Patients.birthdate,
            Patients.avatar,
            Users.username,
            Users.gender,
            Users.email,
            Medical_Info.blood_group,
            Medical_Info.height_cm,
            Medical_Info.weight_kg,
            Medical_Info.allergies,
            Medical_Info.medical_conditions,
        )
        .first_or_404()
    )

    files: Patient_Record_Files = (
        Patient_Record_Files.query.filter(
            Patient_Record_Files.record_patient_id == int(id)
        )
        .order_by(Patient_Record_Files.file_id.desc())
        .paginate(page=page_num, per_page=10)
    )

    return render_template(
        "manager/view_patient.html",
        title=f"{patient.last_name} {patient.first_name}",
        patient=patient,
        files=files,
    )

@manager.route("/dashboard/manager/patients/<id>/delete")
def delete_patient(id):
    if current_user.role != "Manager":
        abort(403)

    user: Users = Users.query.filter(Users.id == int(id)).first_or_404()
    db.session.delete(user)

    date, time = get_datetime()
    new_log: User_Logs = User_Logs(current_user.id, "Delete Patient", date, time)
    new_log.log_desc = f"#{user.id} {user.username}({user.gender}, {user.email})"
    db.session.add()
    db.session.commit()

    flash("Patient deleted successfully!", category="warning")
    return redirect(url_for("manager.patients"))


@manager.route("/dashboard/manager/patients/<patient_id>/records/<file_id>")
@login_required
def view_patient_record_file(patient_id, file_id):
    if current_user.role != "Manager":
        abort(403)

    patient = Patients.query.filter(Patients.p_id == int(patient_id)).first_or_404()
    file: Patient_Record_Files = Patient_Record_Files.query.filter(
        Patient_Record_Files.file_id == int(file_id)
    ).first_or_404()

    return render_template(
        "manager/patient_record_file_view.html",
        patient=patient,
        file=file,
        title=f"{file.file_name}",
    )


@manager.route("/dashboard/manager/patients/<patient_id>/records/<file_id>/delete")
@login_required
def delete_patient_record_file(patient_id, file_id):
    if current_user.role != "Manager":
        abort(403)

    file: Patient_Record_Files = Patient_Record_Files.query.filter_by(
        file_id=int(file_id)
    ).first_or_404()

    if file.record_patient_id == int(patient_id):
        date, time = get_datetime()
        new_log = User_Logs(current_user.id, "Delete Patient Record", date, time)
        new_log.log_desc = f"Patient #{patient_id}, File:{file.file_name}({file.file_size_kb} KB), {file.file_path_name}"

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
        return redirect(url_for("manager.view_patient", id=int(patient_id)))
    else:
        flash("Delete failed! Permission unmatch", category="danger")
        return redirect(url_for("manager.view_patient", id=int(patient_id)))


@manager.route("/dashboard/manager/patients/<id>/appointments")
@login_required
def view_patient_appointments(id):
    if current_user.role != "Manager":
        abort(403)

    page_num = request.args.get("page", 1, int)

    patient: Patients = Patients.query.filter(Patients.p_id == int(id)).first_or_404()
    appointments = (
        Appointments.query.filter(Appointments.appt_patient_id == patient.p_id)
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
        "manager/patient_appointments.html",
        patient=patient,
        appointments=appointments,
        title=f"Patient Appointment History",
    )


@manager.route("/dashboard/manager/patients/<id>/tests")
@login_required
def view_patient_tests(id):
    if current_user.role != "Manager":
        abort(403)

    page_num = request.args.get("page", 1, int)

    patient: Patients = Patients.query.filter(Patients.p_id == int(id)).first_or_404()
    tests = (
        Medical_Test_Book.query.filter(
            Medical_Test_Book.test_patient_id == Patients.p_id
        )
        .filter(Medical_Test_Book.test_patient_id == patient.p_id)
        .join(Invoice_Items, Invoice_Items.item_id == Medical_Test_Book.invoice_item_id)
        .join(Invoices, Invoices.invoice_id == Invoice_Items.invoice_id)
        .order_by(Invoices.invoice_date.desc())
        .add_columns(
            Medical_Test_Book.serial_number,
            Medical_Test_Book.test_status,
            Invoice_Items.item_desc,
            Invoices.invoice_date,
        )
        .paginate(page=page_num, per_page=12)
    )

    return render_template(
        "manager/patient_test_history.html",
        patient=patient,
        tests=tests,
        title=f"{patient.last_name}'s Medical Test History",
    )


@manager.route("/dashboard/manager/patients/<id>/invoices")
@login_required
def view_patient_invoices(id):
    if current_user.role != "Manager":
        abort(403)

    page_num = request.args.get("page", 1, int)

    patient: Patients = Patients.query.filter(Patients.p_id == int(id)).first_or_404()
    invoices = (
        Invoices.query.filter_by(invoice_patient_id=int(id))
        .order_by(Invoices.invoice_id.desc())
        .paginate(page=page_num, per_page=12)
    )

    return render_template(
        "manager/patient_invoices.html",
        patient=patient,
        invoices=invoices,
        title=f"{patient.last_name}'s Invoices",
    )


@manager.route("/dashboard/manager/patients/<id>/logs")
@login_required
def view_patient_logs(id):
    if current_user.role != "Manager":
        abort(403)

    page_num = request.args.get("page", 1, int)

    patient: Patients = Patients.query.filter(Patients.p_id == int(id)).first_or_404()
    logs = (
        User_Logs.query.filter_by(user_id=int(id))
        .order_by(User_Logs.log_id.desc())
        .paginate(page=page_num, per_page=12)
    )

    return render_template(
        "manager/patient_logs.html",
        patient=patient,
        logs=logs,
        title=f"{patient.last_name}'s Account Logs",
    )


# Activity Logs
@manager.route("/dashboard/manager/logs", methods=["GET", "POST"])
@login_required
def logs():
    if current_user.role != "Manager":
        abort(403)

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
        .paginate(page=page_num, per_page=20)
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
    if current_user.role != "Manager":
        abort(403)

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
    if current_user.role != "Manager":
        abort(403)

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
            if profile.avatar == "manager.svg":
                # Store the new picture in the file system
                avatar = profile_picture_saver(form.avatar.data, "manager")
            else:
                # Remove old picture
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
        "manager/account.html",
        title="My Account",
        profile=profile,
        logs=logs,
        form=form,
    )


# Self Change Password
@manager.route("/dashboard/manager/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if current_user.role != "Manager":
        abort(403)

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
