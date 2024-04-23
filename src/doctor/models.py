from src import db

class Doctor_Time(db.Model):
    """
    #### status
        - Unavailable
        - Available
    """

    __tablename__ = "doctor_time"

    doctor_id = db.Column(
        db.Integer, db.ForeignKey("doctors.d_id"), primary_key=True, nullable=False
    )
    day_time_slot = db.Column(db.JSON, nullable=True)
    appt_status = db.Column(db.String(15), nullable=False)

    def __init__(self, doctor_id) -> None:
        super().__init__()
        self.doctor_id = doctor_id
        self.appt_status = "Available"


class Appointments(db.Model):
    __tablename__ = "appointments"

    appt_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    appt_doctor_id = db.Column(
        db.Integer, db.ForeignKey("doctors.d_id"), primary_key=True, nullable=False
    )
    appt_patient_id = db.Column(
        db.Integer, db.ForeignKey("patients.p_id"), primary_key=True, nullable=False
    )

    def __init__(self, doctor_id, patient_id) -> None:
        super().__init__()
        self.appt_doctor_id = doctor_id
        self.appt_patient_id = patient_id

    def __str__(self) -> str:
        return f"#{self.appt_id}: Doctor #{self.appt_doctor_id}, Patient #{self.appt_patient_id}"


class Appointment_Details(db.Model):
    """
    #### appt_status
        - Booked
        - Cancelled
        - Done
    """

    __tablename__ = "appointment_details"

    appt_detail_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    appt_id = db.Column(
        db.Integer,
        db.ForeignKey("appointments.appt_id"),
        primary_key=True,
        nullable=False,
    )
    appt_status = db.Column(db.String(50), nullable=False)
    appt_date = db.Column(db.Date, nullable=False)
    appt_time = db.Column(db.Time, nullable=False)
    appt_time = db.Column(db.String(10), nullable=False)

    def __init__(self, appt_id, appt_status, date, time) -> None:
        super().__init__()
        self.appt_id = appt_id
        self.appt_status = appt_status
        self.appt_date = date
        self.appt_time = time

    def __str__(self) -> str:
        return f"#{self.appt_detail_id} @ Appointment #{self.appt_id} ({self.appt_status}) {self.appt_date}, {self.appt_time} "
