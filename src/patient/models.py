from src import db

# Models that represents database tables


class Medical_Info(db.Model):
    __tablename__ = "medical_info"

    med_info_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer, db.ForeignKey("patients.p_id"), primary_key=True, nullable=False
    )
    blood_group = db.Column(db.String(20), nullable=True)
    height_cm = db.Column(db.Float, nullable=True)
    weight_kg = db.Column(db.Float, nullable=True)
    allergies = db.Column(db.String(255), nullable=True)
    medical_conditions = db.Column(db.String(255), nullable=True)

    def __init__(self, patient_id):
        super().__init__()
        self.patient_id = patient_id

    def __str__(self) -> str:
        return f"MED_INFO({self.med_info_id}) @ Patient #{self.patient_id}"


class Patient_Record_Files(db.Model):
    __tablename__ = "patient_record_files"

    file_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    record_patient_id = db.Column(
        db.Integer, db.ForeignKey("patients.p_id"), primary_key=True, nullable=False
    )
    file_name = db.Column(db.String(100), nullable=False)
    file_path_name = db.Column(db.String(100), nullable=False)
    file_size_kb = db.Column(db.Float, nullable=False)
    upload_date = db.Column(db.Date, nullable=False)
    upload_time = db.Column(db.Time, nullable=False)

    def __init__(
        self,
        record_patient_id,
        file_name,
        file_path_name,
        file_size_kb,
        upload_date,
        upload_time,
    ):
        super().__init__()
        self.record_patient_id = record_patient_id
        self.file_name = file_name
        self.file_path_name = file_path_name
        self.file_size_kb = file_size_kb
        self.upload_date = upload_date
        self.upload_time = upload_time

    def __str__(self) -> str:
        return f"Record File: #{self.file_id} {self.file_name} ({self.file_size_kb} KB) on {self.upload_date}, {self.upload_time}"


class Invoices(db.Model):
    """
    #### status
        - Paid
        - Unpaid
    """

    __tablename__ = "invoices"

    invoice_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    invoice_patient_id = db.Column(
        db.Integer, db.ForeignKey("patients.p_id"), primary_key=True, nullable=False
    )
    total_amount = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(10), nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    invoice_time = db.Column(db.Time, nullable=False)

    def __init__(self, invoice_patient_id, status, invoice_date, invoice_time) -> None:
        super().__init__()
        self.invoice_patient_id = invoice_patient_id
        self.status = status
        self.invoice_date = invoice_date
        self.invoice_time = invoice_time

    def __str__(self) -> str:
        return f"#{self.invoice_id} {self.total_amount} ({self.status}) on {self.invoice_date}, {self.invoice_time}"


class Invoice_Items(db.Model):
    __tablename__ = "invoice_items"

    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    invoice_id = db.Column(
        db.Integer,
        db.ForeignKey("invoices.invoice_id"),
        primary_key=True,
        nullable=False,
    )
    test_id_ref = db.Column(
        db.Integer,
        db.ForeignKey("medical_tests.test_id"),
        primary_key=True,
        nullable=False,
    )
    item_desc = db.Column(db.TEXT, nullable=False)
    item_price = db.Column(db.Float, nullable=False)

    def __init__(self, invoice_id, test_id_ref, item_desc, item_price) -> None:
        super().__init__()
        self.invoice_id = invoice_id
        self.test_id_ref = test_id_ref
        self.item_desc = item_desc
        self.item_price = item_price

    def __str__(self) -> str:
        return f"#{self.item_id} {self.item_desc} ({self.item_price} @ Invoice #{self.invoice_id})"


class Pending_Items(db.Model):
    __tablename__ = "pending_items"

    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_test_id = db.Column(
        db.Integer,
        db.ForeignKey("medical_tests.test_id"),
        primary_key=True,
        nullable=False,
    )
    item_user_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.p_id"),
        primary_key=True,
        nullable=False,
    )
    item_desc = db.Column(db.TEXT, nullable=False)
    item_price = db.Column(db.Float, nullable=False)

    def __init__(self, item_test_id, item_user_id, item_desc, item_price) -> None:
        super().__init__()
        self.item_test_id = item_test_id
        self.item_user_id = item_user_id
        self.item_desc = item_desc
        self.item_price = item_price

    def __str__(self) -> str:
        return f"#{self.item_id} {self.item_desc} ({self.item_price} by User #{self.item_user_id}"


class Payments(db.Model):
    """
    #### payment_method
        - Cash
        - Online
        - Other
    """

    __tablename__ = "payments"

    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    payment_invoice_id = db.Column(
        db.Integer,
        db.ForeignKey("invoices.invoice_id"),
        primary_key=True,
        nullable=False,
    )
    payment_manager_id = db.Column(
        db.Integer,
        db.ForeignKey("managers.m_id"),
        primary_key=True,
        nullable=False,
    )
    payment_amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_time = db.Column(db.Time, nullable=False)
    payment_method = db.Column(db.String(10), nullable=True)
    payment_note = db.Column(db.String(255), nullable=True)

    def __init__(
        self,
        payment_invoice_id,
        payment_manager_id,
        payment_amount,
        payment_date,
        payment_time,
    ) -> None:
        super().__init__()
        self.payment_invoice_id = payment_invoice_id
        self.payment_manager_id = payment_manager_id
        self.payment_amount = payment_amount
        self.payment_date = payment_date
        self.payment_time = payment_time

    def __str__(self) -> str:
        return f"#{self.payment_id} Invoice #{self.payment_invoice_id} ({self.payment_amount}) on {self.payment_date}, {self.payment_date}"


class Medical_Tests(db.Model):
    __tablename__ = "medical_tests"

    test_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    test_name = db.Column(db.String(200), nullable=False)
    test_price = db.Column(db.Float, nullable=False)
    add_date = db.Column(db.Date, nullable=True)
    add_time = db.Column(db.Time, nullable=True)
    test_desc = db.Column(db.TEXT, nullable=True)

    def __init__(
        self, test_name, test_price, add_date, add_time, test_desc=None
    ) -> None:
        super().__init__()
        self.test_name = test_name
        self.test_price = test_price
        self.add_date = add_date
        self.add_time = add_time
        self.test_desc = test_desc

    def __str__(self) -> str:
        return f"#{self.test_id} {self.test_name} ({self.test_price}) on {self.add_date}, {self.add_time}"


class Medical_Test_Book(db.Model):
    """
    #### test_status
        - Pending (Default)
        - Done
    """
    
    __tablename__ = "medical_test_book"

    serial_number = db.Column(db.Integer, primary_key=True, autoincrement=True)
    invoice_item_id = db.Column(
        db.Integer,
        db.ForeignKey("invoice_items.item_id"),
        primary_key=True,
        nullable=False,
    )
    test_patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.p_id"),
        primary_key=True,
        nullable=False,
    )
    test_status = db.Column(db.String(15), nullable=True)

    def __init__(self, invoice_item_id, test_patient_id) -> None:
        super().__init__()
        self.invoice_item_id = invoice_item_id
        self.test_patient_id = test_patient_id
        self.test_status = "Pending"

    def __str__(self) -> str:
        return (
            f"#{self.serial_number} @ {self.item_test_ref_id} by {self.test_patient_id} ({self.test_status})"
        )


class Medical_Report_Files(db.Model):
    __tablename__ = "medical_report_files"

    file_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    test_book_serial = db.Column(
        db.Integer,
        db.ForeignKey("medical_test_book.serial_number"),
        primary_key=True,
        nullable=False,
    )
    file_name = db.Column(db.String(100), nullable=False)
    file_path_name = db.Column(db.String(100), nullable=False)
    file_size_kb = db.Column(db.Float, nullable=False)
    upload_manager_id = db.Column(
        db.Integer,
        db.ForeignKey("managers.m_id"),
        primary_key=True,
        nullable=False,
    )
    upload_date = db.Column(db.Date, nullable=False)
    upload_time = db.Column(db.Time, nullable=False)

    def __init__(
        self,
        test_book_serial,
        file_name,
        file_path_name,
        file_size_kb,
        upload_manager_id,
        upload_date,
        upload_time,
    ):
        super().__init__()
        self.test_book_serial = test_book_serial
        self.file_name = file_name
        self.file_path_name = file_path_name
        self.file_size_kb = file_size_kb
        self.upload_manager_id = upload_manager_id
        self.upload_date = upload_date
        self.upload_time = upload_time

    def __str__(self) -> str:
        return f"Report File: #{self.file_id} {self.file_name} ({self.file_size_kb} KB) on {self.upload_date}, {self.upload_time}"


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
