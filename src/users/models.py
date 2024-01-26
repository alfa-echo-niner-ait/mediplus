from src import db
from flask_login import UserMixin

# Models that represents database tables

class Users(db.Model, UserMixin):
    '''
    #### Users has 3 types of role:
        - Patient
        - Doctor
        - Manager
        
    Default -> Patient
    '''
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    
    def __init__(self, username, pass_hash, email, role="Patient"):
        super().__init__()
        self.username = username
        self.password_hash = pass_hash
        self.email = email
        self.role = role
    
    def get_id(self):
        return self.id
    
    def __str__(self) -> str:
        return f"User({self.id}): {self.username}, {self.role}"
    
    
class Patients(db.Model):
    __tablename__ = "patients"

    p_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                     primary_key=True, nullable=False)
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    birthdate = db.Column(db.Date, nullable=True)
    avatar = db.Column(db.String(100), nullable=True)
    
    def __init__(self, p_id, fname, lname, phone, bdate, avatar="p_default.jpg"):
        super().__init__()
        self.p_id = p_id
        self.first_name = fname
        self.last_name = lname
        self.phone = phone
        self.birthdate = bdate
        self.avatar = avatar
        
    def __str__(self) -> str:
        return f"Patient({self.p_id}): {self.last_name} {self.first_name}"


class Doctors(db.Model):
    __tablename__ = "doctors"

    d_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                     primary_key=True, nullable=False)
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    birthdate = db.Column(db.Date, nullable=True)
    avatar = db.Column(db.String(100), nullable=True)
    title = db.Column(db.String(100), nullable=True)

    def __init__(self, d_id, fname, lname, phone, bdate, title, avatar="d_default.jpg"):
        super().__init__()
        self.d_id = d_id
        self.first_name = fname
        self.last_name = lname
        self.phone = phone
        self.birthdate = bdate
        self.avatar = avatar
        self.title = title

    def __str__(self) -> str:
        return f"Doctor({self.d_id}): {self.last_name} {self.first_name}, {self.title}"
    

class Managers(db.Model):
    __tablename__ = "managers"

    m_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                     primary_key=True, nullable=False)
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    avatar = db.Column(db.String(100), nullable=True)

    def __init__(self, m_id, fname, lname, phone, avatar="m_default.jpg"):
        super().__init__()
        self.m_id = m_id
        self.first_name = fname
        self.last_name = lname
        self.phone = phone
        self.avatar = avatar

    def __str__(self) -> str:
        return f"Manager({self.d_id}): {self.last_name} {self.first_name}"
