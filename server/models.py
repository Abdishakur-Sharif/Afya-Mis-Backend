from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, Enum
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

# Define metadata for naming conventions (including foreign key names)
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

# Initialize the SQLAlchemy object
db = SQLAlchemy(metadata=metadata)


# Doctors Model
class Doctor(db.Model, SerializerMixin):  # Table: 'doctors'
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    phone_number = db.Column(db.String, nullable=False, unique=True)
    speciality = db.Column(db.String, nullable=False)

    # Relationships
    appointments = db.relationship('Appointment', back_populates='doctor')
    diagnosis = db.relationship('Diagnosis', back_populates='doctor')
    prescriptions = db.relationship('Prescription', back_populates='doctor')
    consultations = db.relationship('Consultation', back_populates='doctor')

    serialize_rules = ('-appointments.doctor', '-diagnosis.doctor', '-prescriptions.doctor', '-consultations.doctor')


# Staff Model
class Staff(db.Model, SerializerMixin):  # Table: 'staff'
    __tablename__ = 'staffs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    phone_number = db.Column(db.String, nullable=False, unique=True)
    role = db.Column(db.String, nullable=False) 



# LabTech Model
class LabTech(db.Model, SerializerMixin):  # Table: 'lab_techs'
    __tablename__ = 'lab_techs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)

    # Relationships
    tests = db.relationship('Test', back_populates='lab_tech')

    serialize_rules = ( '-tests.lab_tech')


# Patient Model
class Patient(db.Model, SerializerMixin):  # Table: 'patients'
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    phone_number = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    address = db.Column(db.String, nullable=False,default="")
    gender = db.Column(db.String, nullable=False)
    medical_history = db.Column(db.String)
    

    # Relationships
    appointments = db.relationship('Appointment', back_populates='patient',cascade="all, delete-orphan")
    tests = db.relationship('Test', back_populates='patient',cascade="all, delete-orphan")
    prescriptions = db.relationship('Prescription', back_populates='patient',cascade="all, delete-orphan")
    payments = db.relationship('Payment', back_populates='patient',cascade="all, delete-orphan")
    consultations = db.relationship('Consultation', back_populates='patient',cascade="all, delete-orphan")
    diagnosis = db.relationship('Diagnosis', back_populates='patient',cascade="all, delete-orphan")
    consultation_notes = db.relationship('ConsultationNotes', back_populates='patient',cascade="all, delete-orphan")
    diagnosis_notes = db.relationship('DiagnosisNotes', back_populates='patient',cascade="all, delete-orphan")

    serialize_rules = ('-appointments.patient', '-tests.patient', '-diagnosis.patient', '-prescriptions.patient', '-payments.patient', '-consultations.patient', '-consultation_notes.patient', '-diagnosis_notes.patient')  # Updated serialization rules



# Appointment Model
class Appointment(db.Model, SerializerMixin):  # Table: 'appointments'
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_time = db.Column(db.DateTime, nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)

    # Relationships
    patient = db.relationship('Patient', back_populates='appointments')
    doctor = db.relationship('Doctor', back_populates='appointments')

    serialize_rules = ('-patient.appointments', '-doctor.appointments')


# Test Model
class Test(db.Model, SerializerMixin):  # Table: 'tests'
    __tablename__ = 'tests'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    lab_tech_id = db.Column(db.Integer, db.ForeignKey('lab_techs.id'), nullable=False)
    test_types_id = db.Column(db.Integer, db.ForeignKey('test_types.id'), nullable=False)
    status = db.Column(Enum('pending', 'completed', name='test_status'), nullable=False, server_default='pending')
    test_results = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)

    # Relationships
    patient = db.relationship('Patient', back_populates='tests')
    lab_tech = db.relationship('LabTech', back_populates='tests')
    test_types = db.relationship('TestType', back_populates='tests')

    serialize_only = ('id', 'patient_id', 'doctor_id', 'lab_tech_id', 'test_types_id', 'status', 'created_at')


# TestTypes Model
class TestType(db.Model, SerializerMixin):  # Table: 'test_types'
    __tablename__ = 'test_types'

    id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    price = db.Column(db.Numeric, nullable=False)

    # Relationships
    tests = db.relationship('Test', back_populates='test_types')

    serialize_only = ('id', 'test_name', 'description', 'price', 'tests.id')


# Consultation Model
class Consultation(db.Model, SerializerMixin):  # Table: 'consultations'
    __tablename__ = 'consultations'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    consultation_date = db.Column(db.DateTime, nullable=False)
    
    # Relationships
    patient = db.relationship('Patient', back_populates='consultations')  # Reverse relationship to Patient
    doctor = db.relationship('Doctor', back_populates='consultations')
    consultation_notes = db.relationship('ConsultationNotes', back_populates='consultation')

    serialize_only = (
        'id', 'patient_id', 'doctor_id', 'consultation_date',
        'patient.name'
    )


class ConsultationNotes(db.Model, SerializerMixin):
    __tablename__ = 'consultation_notes'

    id = db.Column(db.Integer, primary_key = True)
    notes = db.Column(db.Text, nullable = False)
    consultation_id = db.Column(db.Integer, db.ForeignKey('consultations.id'), nullable = False)
    created_at = db.Column(db.DateTime)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    # Relationships
    consultation = db.relationship('Consultation', back_populates='consultation_notes')
    patient = db.relationship('Patient', back_populates='consultation_notes')

    # serilaization rules
    serialize_rules = ('-patient.consultation_notes',)

# Diagnosis Model
class Diagnosis(db.Model, SerializerMixin):  # Table: 'diagnosis'
    __tablename__ = 'diagnosis'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    diagnosis_description = db.Column(db.String(255)) 
    created_at = db.Column(db.DateTime, nullable=False)

    # Relationships
    patient = db.relationship('Patient', back_populates='diagnosis')
    doctor = db.relationship('Doctor', back_populates='diagnosis')
    diagnosis_notes = db.relationship('DiagnosisNotes', back_populates='diagnosis')

    serialize_only = (
        'id', 'patient_id', 'doctor_id', 
        'created_at','diagnosis_description'
    )


class DiagnosisNotes(db.Model, SerializerMixin):
    __tablename__ = 'diagnosis_notes'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime)
    diagnosis_id = db.Column(db.Integer, db.ForeignKey('diagnosis.id'), nullable=False)
    notes = db.Column(db.Text, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    # Relationships
    diagnosis = db.relationship('Diagnosis', back_populates='diagnosis_notes')
    patient = db.relationship('Patient', back_populates='diagnosis_notes')


    # Serialization rules
    serialize_rules = ('-patient.diagnosis_notes',)


# Prescription Model
class Prescription(db.Model, SerializerMixin):  # Table: 'prescriptions'
    __tablename__ = 'prescriptions'

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    dosage = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    prescription_date = db.Column(db.DateTime, nullable=False)

    # Relationships
    patient = db.relationship('Patient', back_populates='prescriptions')
    doctor = db.relationship('Doctor', back_populates='prescriptions')
    medicine = db.relationship('Medicine', back_populates='prescriptions')

    serialize_only = (
        'id', 'appointment_id', 'patient_id', 'doctor_id', 'medicine_id',
        'dosage', 'quantity', 'duration', 'prescription_date'
    )


# Medicine Model
class Medicine(db.Model, SerializerMixin):  # Table: 'medicines'
    __tablename__ = 'medicines'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)

    # Relationships
    prescriptions = db.relationship('Prescription', back_populates='medicine')

    serialize_only = ('id', 'name', 'description')


# Payments Model
class Payment(db.Model, SerializerMixin):  # Table: 'payments'
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    service = db.Column(db.String, nullable=False)
    amount = db.Column(db.Numeric, nullable=False)

    # Relationships
    patient = db.relationship('Patient', back_populates='payments')

    serialize_rules = ('-patient.payments', )
