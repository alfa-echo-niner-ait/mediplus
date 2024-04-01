import os
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
from src.users.models import Users, User_Logs, Patients, Doctors, Managers
from src.patient.models import (
    Invoices,
    Invoice_Items,
    Payments,
    Medical_Tests,
    Medical_Test_Book,
    Medical_Report_Files,
)
from .forms import (
    LogSortForm,
    ChangePasswordForm,
    SelfProfileForm,
    NewMedicalTestForm,
    UpdateMedicalTestForm,
    UpdateInvoiceForm,
    Test_Result_Upload_Form,
    RegisterDoctorForm,
)
from src.public.forms import SearchTestForm
from src import db, hash_manager
from src.public.utils import (
    get_datetime,
    profile_picture_saver,
    profile_picture_remover,
)

# Declare Blueprint
manager = Blueprint("manager", __name__)


@manager.route("/dashboard/manager")
@login_required
def dashboard():
    return render_template("manager/dashboard.html", title="Manager Dashboard")


@manager.route("/dashboard/appointments")
@login_required
def appointemnts():
    return render_template("manager/appointments.html", title="Appointments Management")


@manager.route("/dashboard/manager/tests", methods=["GET", "POST"])
@login_required
def tests():
    page_num = request.args.get("page", 1, int)

    items = (
        Medical_Test_Book.query.join(
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
            Invoices.status,
            Invoices.invoice_date,
            Invoices.invoice_time,
        )
        .paginate(page=page_num, per_page=15)
    )

    return render_template(
        "manager/tests.html",
        items=items,
        title="Tests Management",
    )


@manager.route("/dashboard/manager/tests/<serial_number>", methods=["GET", "POST"])
@login_required
def test_details(serial_number):
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


@manager.route("/dashboard/manager/invoices")
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
    page_num = request.args.get("page", 1, int)

    doctors = (
        Doctors.query.join(Users, Doctors.d_id == Users.id)
        .add_columns(
            Users.username,
            Users.email,
            Users.gender,
            Doctors.d_id,
            Doctors.title,
            Doctors.first_name,
            Doctors.last_name,
            Doctors.phone,
            Doctors.birthdate,
            Doctors.avatar,
        )
        .paginate(page=page_num, per_page=12)
    )

    return render_template("manager/doctors.html", doctors=doctors, title="Doctors")


@manager.route("/dashboard/manager/doctors/register", methods=["GET", "POST"])
@login_required
def register_doctor():
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
            avatar = "doc_male.svg"
        else:
            avatar = "doc_female.svg"

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

        # Create Log
        date, time = get_datetime()
        new_log = User_Logs(new_doctor.d_id, "New Doctor Registration", date, time)
        new_log.log_desc = (
            f"Registered New Doctor #{new_doctor.d_id} by Manager #{current_user.id}"
        )
        db.session.add(new_log)
        db.session.commit()

        flash("New Doctor Registered Successfully!", category="success")
        return redirect(url_for("manager.doctors"))

    return render_template(
        "manager/register_doctor.html", form=form, title="Register New Doctors"
    )


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
