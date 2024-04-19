from src import db

class Doctor_Time(db.Model):
    __tablename__ = "doctor_time"

    doctor_id = db.Column(
        db.Integer, db.ForeignKey("doctors.d_id"), primary_key=True, nullable=False
    )
    day_time_slot = db.Column(db.JSON)

    def __init__(self, doctor_id) -> None:
        super().__init__()
        self.doctor_id = doctor_id
