from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    session,
)
from flask_login import current_user, login_user, login_required, logout_user
from src.public.forms import (
    LoginForm,
    RegisterForm,
    ResetRequestForm,
    ResetPasswordForm,
    SearchTestForm,
    SearchDoctorForm,
    AppointmentForm,
)
from src.public.utils import get_datetime
from src.users.models import Users, Patients, User_Logs, Managers, Doctors
from src.doctor.models import Doctor_Time, Appointments, Appointment_Details
from src.patient.models import (
    Medical_Info,
    Invoices,
    Invoice_Items,
    Payments,
    Medical_Tests,
    Pending_Items,
)
from src.users.utils import reset_mail_sender
from src import db, token_manager, hash_manager

public = Blueprint("public", __name__)


@public.route("/", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        if current_user.role == "Patient":
            session["pending_items"] = Pending_Items.query.filter_by(
                item_user_id=current_user.id).count()
        if "avatar" not in session:
            if current_user.role == "Patient":
                patient = Patients.query.filter_by(
                    p_id=current_user.id).first()
                session["avatar"] = patient.avatar
            elif current_user.role == "Manager":
                manager = Managers.query.filter_by(
                    m_id=current_user.id).first()
                session["avatar"] = manager.avatar
            elif current_user.role == "Doctor":
                doctor = Doctors.query.filter_by(d_id=current_user.id).first()
                session["avatar"] = doctor.avatar

    return render_template("public/index.html")


@public.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user: Users

        login_with = form.login_with.data
        account = form.account.data
        password = form.password.data
        remember = form.remember.data

        if login_with == "username":
            user = Users.query.filter_by(username=account).first()
        elif login_with == "email":
            user = Users.query.filter_by(email=account).first()

        if user and hash_manager.check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)

            if user.role == "Patient":
                patient = Patients.query.filter_by(p_id=user.id).first()
                session["avatar"] = patient.avatar
                session["pending_items"] = Pending_Items.query.filter_by(
                    item_user_id=current_user.id).count()
            elif user.role == "Manager":
                manager = Managers.query.filter_by(m_id=user.id).first()
                session["avatar"] = manager.avatar
            elif user.role == "Doctor":
                doctor = Doctors.query.filter_by(d_id=user.id).first()
                session["avatar"] = doctor.avatar

            date, time = get_datetime()

            new_log = User_Logs(current_user.id, "Login", date, time)
            new_log.log_desc = f"IP: {request.remote_addr}, Device: {
                request.headers.get("User-Agent")}"

            db.session.add(new_log)
            db.session.commit()

            return redirect(url_for("public.dashboard"))

    return render_template("public/login.html", form=form, title="Login")


@public.route("/logout")
def logout():
    date, time = get_datetime()
    new_log = User_Logs(current_user.id, "Logout", date, time)
    new_log.log_desc = f"IP: {request.remote_addr}, Device: {
        request.headers.get("User-Agent")}"

    db.session.add(new_log)
    db.session.commit()

    session.pop("avatar", None)
    session.pop("pending_items", None)

    logout_user()
    flash("Logout successfull!", category="warning")
    return redirect(url_for("public.index"))


@public.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        gender = form.gender.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        birthdate = form.birthdate.data

        avatar = "user_male.svg" if gender == "Male" else "user_female.svg"
        password_hash = hash_manager.generate_password_hash(
            password).decode("utf-8")
        date, time = get_datetime()

        new_user = Users(username, password_hash, email, gender, "Patient")
        db.session.add(new_user)
        db.session.commit()

        user = Users.query.filter_by(username=username).first()
        new_patient = Patients(user.id, first_name,
                               last_name, birthdate, avatar)
        new_log = User_Logs(user.id, "Registration", date, time)
        new_log.log_desc = f"IP: {request.remote_addr}, Device: {
            request.headers.get("User-Agent")}"

        db.session.add(new_patient)
        db.session.add(new_log)
        db.session.commit()

        patient = Patients.query.filter_by(p_id=user.id).first()
        new_info = Medical_Info(patient.p_id)
        db.session.add(new_info)
        db.session.commit()

        flash("Registration successfull! Login to continue.", category="success")
        return redirect(url_for("public.login"))

    return render_template("public/register.html", form=form, title="Registration")


@public.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    form = ResetRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        user = Users.query.filter_by(email=email).first()

        if user:
            token = token_manager.sign(f"{user.role}{user.email}{user.id}").decode(
                "utf-8"
            )
            user.token = token
            reset_mail_sender(user)

            date, time = get_datetime()
            new_log = User_Logs(user.id, "Password Reset Request", date, time)
            new_log.log_desc = f"IP: {request.remote_addr}, Device: {
                request.headers.get("User-Agent")}"

            db.session.add(new_log)
            db.session.commit()

            flash("Password reset link sent to your email!", category="success")
        else:
            flash("Sorry, no user found with this email!", category="warning")
        return redirect(url_for("public.reset_request"))

    return render_template(
        "public/reset_request.html", form=form, title="Reset Password"
    )


@public.route("/reset_password/<username>/<token>", methods=["GET", "POST"])
def reset_password(username, token):
    form = ResetPasswordForm()
    user = Users.query.filter_by(username=username).first()

    if request.method == "GET":
        if user and user.validate_token(token):
            return render_template(
                "public/reset_password.html", form=form, title="Change Password"
            )
        else:
            flash("Reset link error or timedout! Please try again!",
                  category="danger")
            return redirect(url_for("public.reset_request"))

    if form.validate_on_submit():
        password = form.password.data
        password_hash = hash_manager.generate_password_hash(password).decode(
            "utf-8"
        )

        user.password_hash = password_hash
        user.token = ""

        date, time = get_datetime()
        new_log = User_Logs(user.id, "Change Password", date, time)
        new_log.log_desc = f"IP: {request.remote_addr}, Device: {
            request.headers.get("User-Agent")}"

        db.session.add(new_log)
        db.session.commit()

        flash(
            "Password changed successfully! Login to continue.", category="success"
        )
        return redirect(url_for("public.login"))
    else:
        flash("Sorry, password didn't match!", category="danger")
        return render_template(
            "public/reset_password.html", form=form, title="Change Password"
        )


@public.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "Patient":
        session["pending_items"] = Pending_Items.query.filter_by(
            item_user_id=current_user.id).count()
    if "avatar" not in session:
        if current_user.role == "Patient":
            patient = Patients.query.filter_by(p_id=current_user.id).first()
            session["avatar"] = patient.avatar
        elif current_user.role == "Manager":
            manager = Managers.query.filter_by(m_id=current_user.id).first()
            session["avatar"] = manager.avatar
        elif current_user.role == "Doctor":
            doctor = Doctors.query.filter_by(d_id=current_user.id).first()
            session["avatar"] = doctor.avatar

    if current_user.role == "Patient":
        return redirect(url_for("patient.dashboard"))
    elif current_user.role == "Doctor":
        return redirect(url_for("doctor.dashboard"))
    elif current_user.role == "Manager":
        return redirect(url_for("manager.dashboard"))


@public.route("/invoice/<id>")
def invoice(id):
    # if current_user.role == "Manager":
    #     return redirect(url_for('manager.invoice_update', id=id))

    invoice: Invoices = Invoices.query.filter_by(invoice_id=id).first_or_404()
    patient: Patients = Patients.query.filter_by(
        p_id=invoice.invoice_patient_id).first()
    items: Invoice_Items = Invoice_Items.query.filter_by(invoice_id=id).all()

    url = url_for(
        "public.invoice",
        id=invoice.invoice_id,
        _external=True,
    )
    return render_template(
        "public/invoice.html", title=f"Invoice #{id}", invoice=invoice, patient=patient, items=items, url=url)


@public.route("/tests", methods=["GET", "POST"])
def tests():
    if current_user.is_authenticated and current_user.role == "Patient":
        session["pending_items"] = Pending_Items.query.filter_by(
            item_user_id=current_user.id).count()
    page_num = request.args.get("page", 1, int)
    title = "Medical Tests"
    search = "no"

    form = SearchTestForm()
    tests = Medical_Tests.query.order_by(Medical_Tests.test_name.asc()).paginate(
        page=page_num, per_page=10
    )

    if form.validate_on_submit():
        if page_num > 1:
            page_num = 1
        tests = Medical_Tests.query.filter(
            Medical_Tests.test_name.icontains(
                form.keyword.data) | Medical_Tests.test_desc.icontains(form.keyword.data)
        ).paginate(page=page_num, per_page=15)
        title = f"Search Result: {form.keyword.data}"
        search = "yes"

    return render_template("public/tests.html", form=form, tests=tests, search=search, title=title)


@public.route('/doctors', methods=["GET", "POST"])
def doctors():
    page_num = request.args.get("page", 1, int)
    title = "Doctors List"
    search = "no"
    form = SearchDoctorForm()

    doctors = Doctors.query.join(
        Users, Doctors.d_id == Users.id
    ).join(
        Doctor_Time, Doctors.d_id == Doctor_Time.doctor_id
        ).add_columns(
        Users.gender,
        Doctors.d_id,
        Doctors.first_name,
        Doctors.last_name,
        Doctors.title, Doctors.avatar,
        Doctor_Time.appt_status,
    ).paginate(page=page_num, per_page=12)

    if form.validate_on_submit():
        if page_num > 1:
            page_num = 1
        search = "yes"
        title = f"Search Result: {form.keyword.data}"

        doctors = Doctors.query.filter(
            Doctors.title.icontains(form.keyword.data) | Doctors.last_name.icontains(
                form.keyword.data) | Doctors.first_name.icontains(form.keyword.data)
        ).join(Users, Doctors.d_id == Users.id
               ).add_columns(
            Users.gender,
            Doctors.d_id,
            Doctors.first_name,
            Doctors.last_name,
            Doctors.title,
            Doctors.avatar,
        ).paginate(page=page_num, per_page=12)

    return render_template('public/doctors.html',
                           doctors=doctors, form=form,
                           search=search, title=title)


@public.route('/doctors/<id>')
@login_required
def view_doctor(id):
    doctor = Doctors.query.filter(Doctors.d_id == int(id)).join(
        Users, Doctors.d_id == Users.id).join(Doctor_Time, Doctors.d_id == Doctor_Time.doctor_id).add_columns(
            Users.gender,
            Doctors.d_id,
            Doctors.first_name,
            Doctors.last_name,
            Doctors.title,
            Doctors.avatar,
            Doctor_Time.appt_status,
            Doctor_Time.day_time_slot,
    ).first_or_404()
    
    days = [int(time) for time in doctor.day_time_slot.get("days", [])]
    form = AppointmentForm()
    if request.method == "GET" and doctor.day_time_slot:
        form.times.data = doctor.day_time_slot["times"]

    return render_template(
        'public/doctor_details.html',
        doctor=doctor,
        form=form,
        days=days,
        title=f"Dr. {doctor.last_name} {doctor.first_name}"
        )
    
@public.route('/doctors/<doctor_id>/book_appt', methods=["POST"])
@login_required
def book_appointment(doctor_id):
    form = AppointmentForm()
    if request.method == "POST":
        if form.appt_date.data and form.times.data:
            new_appt: Appointments = Appointments(int(doctor_id), current_user.id)
            db.session.add(new_appt)
            db.session.commit()
            
            new_appt_details: Appointment_Details = Appointment_Details(new_appt.appt_id, "Booked", form.appt_date.data, form.times.data[0])
            db.session.add(new_appt_details)
            db.session.commit()
            
            date, time = get_datetime()
            new_log: User_Logs = User_Logs(current_user.id, "New Appointment", date, time)
            new_log.log_desc = f"Appointment #{new_appt.appt_id}, Detail #{new_appt_details.appt_detail_id}, Doctor #{doctor_id}"
            db.session.add(new_log)
            db.session.commit()

            flash("Booking Appointment Successfull!", category="success")
            return redirect(url_for('public.view_doctor', id=doctor_id))

        else:
            flash("Booking Appointment Failed!", category="danger")
            return redirect(url_for('public.view_doctor', id=doctor_id))
