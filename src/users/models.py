from src import db, token_manager
from flask_login import UserMixin

# Models that represents database tables


class Users(db.Model, UserMixin):
    """
    #### Users has 3 types of role:
        - Patient
        - Doctor
        - Manager

    Default -> Patient
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    token = db.Column(db.String(255), nullable=True)

    def __init__(self, username, pass_hash, email, gender, role="Patient"):
        super().__init__()
        self.username = username
        self.password_hash = pass_hash
        self.email = email
        self.gender = gender
        self.role = role

    def get_id(self):
        return self.id

    def validate_token(self, token, time=600):
        # Default time=600 seconds
        if token == self.token:
            check = token_manager.validate(
                self.token.encode("utf-8"), max_age=time
            )  # Return True/False
            return check
        else:
            return False

    def __str__(self) -> str:
        return f"User({self.id}): {self.username}/{self.gender}, {self.role}"


class User_Logs(db.Model):
    """
    #### log_type
        - Registration
        - Login
        - Change Password
        - Update Profile
    """

    __tablename__ = "user_logs"

    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False
    )
    log_type = db.Column(db.String(100), nullable=False)
    log_date = db.Column(db.Date, nullable=False)
    log_time = db.Column(db.Time, nullable=False)
    log_desc = db.Column(db.TEXT, nullable=True)

    def __init__(self, user_id, log_type, log_date, log_time):
        super().__init__()
        self.user_id = user_id
        self.log_type = log_type
        self.log_date = log_date
        self.log_time = log_time

    def __str__(self) -> str:
        return f"#{self.log_id}:[{self.log_type}] @user_id: {self.user_id} on {self.log_date} {self.log_time}"


class Patients(db.Model):
    """
    #### avatar
        - user_male.svg
        - user_female.svg

        path: /static/avatars/patient
    """

    __tablename__ = "patients"

    p_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False
    )
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    birthdate = db.Column(db.Date, nullable=True)
    avatar = db.Column(db.String(100), nullable=True)

    def __init__(self, p_id, fname, lname, bdate, avatar):
        super().__init__()
        self.p_id = p_id
        self.first_name = fname
        self.last_name = lname
        self.birthdate = bdate
        self.avatar = avatar

    def __str__(self) -> str:
        return f"Patient({self.p_id}): {self.last_name} {self.first_name}"


class Doctors(db.Model):
    """
    #### avatar
        - doctor_male.png
        - doctor_female.png

        path: /static/avatars/doctor
    """

    __tablename__ = "doctors"

    d_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False
    )
    title = db.Column(db.String(100), nullable=True)
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    birthdate = db.Column(db.Date, nullable=True)
    avatar = db.Column(db.String(100), nullable=True)

    def __init__(self, d_id, fname, lname, phone, bdate, title, avatar):
        super().__init__()
        self.d_id = d_id
        self.title = title
        self.first_name = fname
        self.last_name = lname
        self.phone = phone
        self.birthdate = bdate
        self.avatar = avatar

    def __str__(self) -> str:
        return f"Doctor({self.d_id}): {self.last_name} {self.first_name}, {self.title}"


class Managers(db.Model):
    __tablename__ = "managers"

    m_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False
    )
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    birthdate = db.Column(db.Date, nullable=True)
    avatar = db.Column(db.String(100), nullable=True)

    def __init__(self, m_id, fname, lname, phone, birthdate, avatar="manager.svg"):
        super().__init__()
        self.m_id = m_id
        self.first_name = fname
        self.last_name = lname
        self.phone = phone
        self.birthdate = birthdate
        self.avatar = avatar

    def __str__(self) -> str:
        return f"Manager({self.d_id}): {self.last_name} {self.first_name}"


class Appointments(db.Model):
    __tablename__ = "appointments"

    appt_id = db.Column(db.Integer, primary_key=True)
    appt_doctor_id = db.Column(
        db.Integer, db.ForeignKey("doctors.id"), primary_key=True, nullable=False
    )
    appt_patient_id = db.Column(
        db.Integer, db.ForeignKey("patients.id"), primary_key=True, nullable=False
    )

    def __init__(self, doctor_id, patient_id) -> None:
        super().__init__()
        self.appt_doctor_id = doctor_id
        self.appt_patient_id = patient_id

    def __str__(self) -> str:
        return f"#{self.appt_id}: Doctor #{self.appt_doctor_id}, Patient #{self.appt_patient_id}"


class Appointment_Details(db.Model):
    __tablename__ = "appointment_details"

    appt_detail_id = db.Column(db.Integer, primary_key=True)
    appt_id = db.Column(
        db.Integer, db.ForeignKey("appointments.id"), primary_key=True, nullable=False
    )
    appt_status = db.Column(db.String(50), nullable=False)
    appt_date = db.Column(db.Date, nullable=False)
    appt_time = db.Column(db.Time, nullable=False)

    def __init__(self, appt_id, appt_status, date, time) -> None:
        super().__init__()
        self.appt_id = appt_id
        self.appt_status = appt_status
        self.appt_date = date
        self.appt_time = time

    def __str__(self) -> str:
        return f"#{self.appt_detail_id} @ Appointment #{self.appt_id} ({self.appt_status}) {self.appt_date}, {self.appt_time} "
