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
    upload_date = db.Column(db.Date, nullable=False)
    upload_time = db.Column(db.Time, nullable=False)

    def __init__(
        self, record_patient_id, file_name, file_path_name, upload_date, upload_time
    ):
        super().__init__()
        self.record_patient_id = record_patient_id
        self.file_name = file_name
        self.file_path_name = file_path_name
        self.upload_date = upload_date
        self.upload_time = upload_time

    def __str__(self) -> str:
        return f"Record File: #{self.file_id} {self.file_name} on {self.upload_date}, {self.upload_time}"


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

    def __init__(
        self, invoice_patient_id, total_amount, status, invoice_date, invoice_time
    ) -> None:
        super().__init__()
        self.invoice_patient_id = invoice_patient_id
        self.total_amount = total_amount
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
    item_desc = db.Column(db.TEXT, nullable=False)
    item_price = db.Column(db.Float, nullable=False)

    def __init__(self, invoice_id, item_desc, item_price) -> None:
        super().__init__()
        self.invoice_id = invoice_id
        self.item_desc = item_desc
        self.item_price = item_price

    def __str__(self) -> str:
        return f"#{self.item_id} {self.item_desc} ({self.item_price} @ Invoice #{self.invoice_id})"


class Payments(db.Model):
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
