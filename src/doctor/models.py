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
        - Completed
    """

    __tablename__ = "appointment_details"

    appt_detail_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    appt_id = db.Column(
        db.Integer,
        db.ForeignKey("appointments.appt_id"),
        unique=True,
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


class Prescriptions(db.Model):

    __tablename__ = "prescriptions"

    prescription_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    pres_appt_id = db.Column(
        db.Integer, db.ForeignKey("appointments.appt_id"), primary_key=True, unique=True, nullable=False
    )
    pres_date = db.Column(db.Date, nullable=False)
    last_update_date = db.Column(db.Date, nullable=False)
    last_update_time = db.Column(db.Time, nullable=False)

    def __init__(self, appointment_id, date, last_update_date, last_update_time) -> None:
        super().__init__()
        self.pres_appt_id = appointment_id
        self.pres_date = date
        self.last_update_date = last_update_date
        self.last_update_time = last_update_time


class Prescription_Extras(db.Model):

    __tablename__ = "prescription_extras"

    prescription_id = db.Column(
        db.Integer,
        db.ForeignKey("prescriptions.prescription_id"),
        primary_key=True,
        nullable=False,
    )
    diagnosis = db.Column(db.TEXT, nullable=True)
    notes = db.Column(db.TEXT, nullable=True)
    next_meet = db.Column(db.TEXT, nullable=True)

    def __init__(self, pescription_id) -> None:
        super().__init__()
        self.prescription_id = pescription_id


class Prescribed_Items(db.Model):

    __tablename__ = "prescribed_items"

    pres_item_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    item_pres_id = db.Column(
        db.Integer,
        db.ForeignKey("prescriptions.prescription_id"),
        primary_key=True,
        nullable=False,
    )
    medicine = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=True)
    instruction = db.Column(db.String(200), nullable=True)
    duration = db.Column(db.String(50), nullable=True)

    def __init__(self, prescription_id, medicine, dosage, instruction, duration) -> None:
        super().__init__()
        self.item_pres_id = prescription_id
        self.medicine = medicine
        self.dosage = dosage
        self.instruction = instruction
        self.duration = duration
