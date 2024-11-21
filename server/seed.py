from app import app, db
from models import Doctor, Staff, TestReport, LabTech, Patient, Appointment, Test, Consultation, ConsultationNotes, DiagnosisNotes, Diagnosis, Prescription, Payment, TestType, Medicine
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

specialties = [
    "Cardiology", "Dermatology", "Neurology", "Pediatrics", "Orthopedics",
    "Ophthalmology", "Psychiatry", "Radiology", "Gastroenterology", "Endocrinology"
]

conditions = [
    'Hypertension', 'Diabetes', 'Asthma', 'Chronic Back Pain', 'Migraine', 'Anemia', 'Arthritis', 'Allergies'
]

def drop_all_tables():
    with app.app_context():
        db.drop_all()  # Drops all tables in the database
        db.create_all()  # Creates all tables in the database
        print("All tables dropped and recreated successfully.")

def create_doctors():
    for _ in range(10):  # Create 10 doctors
        doctor = Doctor(
            name=fake.name(),
            email=fake.email(),
            phone_number=fake.phone_number(),
            speciality=random.choice(specialties)
        )
        db.session.add(doctor)
    db.session.commit()
    print("Doctors created successfully.")

def create_staffs():
    roles = ['Receptionist', 'Doctor', 'Lab Technician', 'Admin']
    
    for i in range(10):  # Create 10 staff members
        staff = Staff(
            name=fake.name(),
            email=fake.email(),
            phone_number=fake.phone_number(),
            role=random.choice(roles)  # Randomly select a role from the predefined list
        )
        db.session.add(staff)
    
    db.session.commit()
    print("Staffs created successfully.")


def create_lab_techs():
    for _ in range(5):  # Create 5 lab techs
        lab_tech = LabTech(
            name=fake.name(),
            email=fake.email(),
            phone_number=fake.phone_number(),
        )
        db.session.add(lab_tech)
    db.session.commit()
    print("LabTechs created successfully.")

def create_patients():
    for _ in range(20):  # Create 20 patients
        patient = Patient(
            name=fake.name(),
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=80),
            phone_number=fake.phone_number(),
            email=fake.email(),
            address=fake.address(),
            gender=random.choice(['Male', 'Female']),
            medical_history=random.choice(conditions)
        )
        db.session.add(patient)
        db.session.commit()

        # Create an appointment for the patient first
        doctor = random.choice(Doctor.query.all())  # Random doctor
        appointment_date = fake.date_this_year()
        appointment_time_str = fake.time()[:5]  # Truncate to 'HH:MM'

        # Convert time to 12-hour format
        appointment_time_12hr = datetime.strptime(appointment_time_str, '%H:%M').strftime('%I:%M %p')
        appointment_time = datetime.strptime(appointment_time_12hr, '%I:%M %p').time()

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        )
        db.session.add(appointment)
        db.session.commit()  # Ensure the appointment is committed before proceeding

        # Now create consultation for the patient with the appointment_id
        consultation = Consultation(
            patient_id=patient.id,
            doctor_id=doctor.id,
            consultation_date=fake.date_this_year(),
            appointment_id=appointment.id  # Link consultation to the created appointment
        )
        db.session.add(consultation)
        db.session.commit()

        # Create consultation notes
        consultation_notes = ConsultationNotes(
            patient_id=patient.id,
            consultation_id=consultation.id,
            notes=fake.text(),
            created_at=datetime.utcnow()
        )
        db.session.add(consultation_notes)
        db.session.commit()

        # Create diagnosis
        diagnosis = Diagnosis(
            patient_id=patient.id,
            doctor_id=doctor.id,
            created_at=datetime.utcnow(),
            appointment_id=appointment.id  # Link diagnosis to the created appointment
        )
        db.session.add(diagnosis)
        db.session.commit()

        # Create diagnosis notes
        diagnosis_notes = DiagnosisNotes(
            patient_id=patient.id,
            diagnosis_id=diagnosis.id,
            notes=fake.text(),
            created_at=datetime.utcnow()
        )
        db.session.add(diagnosis_notes)
        db.session.commit()

    print("Patients and associated data created successfully.")

def create_medicines():
    medicines = [
        ('Paracetamol', 'Used to relieve pain and reduce fever'),
        ('Ibuprofen', 'Used to reduce fever, pain, and inflammation'),
        ('Amoxicillin', 'An antibiotic used to treat bacterial infections'),
        ('Cetirizine', 'An antihistamine used to relieve allergy symptoms'),
        ('Metformin', 'Used to control high blood sugar in type 2 diabetes'),
        ('Aspirin', 'Used to reduce pain, fever, and inflammation'),
        ('Lisinopril', 'Used to treat high blood pressure and heart failure')
    ]
    for name, description in medicines:
        if not Medicine.query.filter_by(name=name).first():
            medicine = Medicine(name=name, description=description)
            db.session.add(medicine)
    db.session.commit()
    print("Medicines created successfully.")

def create_appointments():
    patients = Patient.query.all()
    doctors = Doctor.query.all()

    for _ in range(5):  # Create 5 appointments
        patient = random.choice(patients)
        doctor = random.choice(doctors)

        appointment_date = fake.date_this_year()
        appointment_time_str = fake.time()[:5]  # Truncate to 'HH:MM'

        # Convert time to 12-hour format
        appointment_time_12hr = datetime.strptime(appointment_time_str, '%H:%M').strftime('%I:%M %p')
        appointment_time = datetime.strptime(appointment_time_12hr, '%I:%M %p').time()

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        )
        db.session.add(appointment)
    db.session.commit()
    print("Appointments created successfully.")

def create_consultations():
    consultations_notes = [
        "Patient presents with a headache and dizziness. Recommended further tests.",
        "Patient shows signs of chronic back pain. Suggested physical therapy.",
        "Patient reports feeling fatigued. Blood tests suggested for anemia.",
        "Patient complains of joint pain and swelling. Arthritis suspected, medication prescribed.",
        "Patient has a persistent cough. Possible asthma attack. Medication prescribed."
    ]

    patients = Patient.query.all()
    doctors = Doctor.query.all()
    appointments = Appointment.query.all()  # Get all appointments

    for _ in range(5):
        patient = random.choice(patients)
        doctor = random.choice(doctors)

        # Ensure there's an appointment to link to the consultation
        appointment = random.choice(appointments)

        consultation = Consultation(
            patient_id=patient.id,
            doctor_id=doctor.id,
            consultation_date=fake.date_this_year(),
            appointment_id=appointment.id  # Set appointment_id to link the consultation
        )
        db.session.add(consultation)
        db.session.commit()

        consultation_notes = ConsultationNotes(
            consultation_id=consultation.id,
            notes=random.choice(consultations_notes),
            created_at=datetime.utcnow(),
            patient_id=patient.id
        )
        db.session.add(consultation_notes)
        db.session.commit()
def create_diagnoses():
    patients = Patient.query.all()
    doctors = Doctor.query.all()

    for _ in range(5):
        patient = random.choice(patients)
        doctor = random.choice(doctors)

        # Ensure the patient has at least one appointment
        appointment = Appointment.query.filter_by(patient_id=patient.id).first()  # Get an appointment for the patient

        if not appointment:
            print(f"Skipping diagnosis creation for patient {patient.id} as no appointment exists.")
            continue  # Skip this patient if no appointment is found

        # Create diagnosis and ensure appointment_id is valid
        diagnosis = Diagnosis(
            patient_id=patient.id,
            doctor_id=doctor.id,
            diagnosis_description=random.choice(conditions),
            created_at=fake.date_this_year(),
            appointment_id=appointment.id  # Link diagnosis to the appointment
        )
        db.session.add(diagnosis)
        db.session.commit()

        # Create diagnosis notes for the diagnosis
        diagnosis_notes = DiagnosisNotes(
            diagnosis_id=diagnosis.id,
            notes=fake.text(),
            created_at=datetime.utcnow(),
            patient_id=patient.id
        )
        db.session.add(diagnosis_notes)
        db.session.commit()

    print("Diagnoses created successfully.")
def create_prescriptions():
    medicines = Medicine.query.all()
    appointments = Appointment.query.all()
    patients = Patient.query.all()
    doctors = Doctor.query.all()

    def get_random_dosage():
        return f"{random.randint(1, 3)} {random.choice(['mg', 'g', 'ml', 'tablet', 'capsules'])}"

    prescriptions = []
    for appointment in appointments:
        # Ensure the doctor and patient are correctly linked to the appointment
        doctor = appointment.doctor
        patient = appointment.patient

        prescription = Prescription(
            appointment_id=appointment.id,
            patient_id=patient.id,
            doctor_id=doctor.id,
            medicine_id=random.choice(medicines).id,
            dosage=get_random_dosage(),
            quantity=random.randint(1, 5),
            duration=random.randint(7, 14),
            prescription_date=fake.date_this_year()
        )

        prescriptions.append(prescription)

    db.session.add_all(prescriptions)
    db.session.commit()
    print("Prescriptions created successfully.")

def create_payments():
    patients = Patient.query.all()
    appointments = Appointment.query.all()  # Get all appointments

    for _ in range(5):
        patient = random.choice(patients)
        
        # Ensure the patient has at least one appointment
        appointment = random.choice([a for a in appointments if a.patient_id == patient.id])

        payment = Payment(
            patient_id=patient.id,
            service=random.choice(['Consultation', 'Lab Test', 'X-Ray', 'Blood Test']),
            amount=random.randint(100, 500),
            payment_method=random.choice(['cash', 'mpesa']),
            appointment_id=appointment.id  # Associate payment with a valid appointment
        )
        db.session.add(payment)
    db.session.commit()
    print("Payments created successfully.")


def create_test_types():
    test_types = [
        ('Blood Test', 'Test to check various blood parameters', 50.0),
        ('X-Ray', 'Imaging test to examine bones and tissues', 100.0),
        ('MRI Scan', 'Magnetic resonance imaging for detailed body scans', 200.0),
        ('CT Scan', 'Computed tomography scan for internal imaging', 150.0),
        ('Urine Test', 'Test to detect infections or kidney issues', 30.0),
        ('ECG', 'Test to check the electrical activity of the heart', 75.0),
        ('Ultrasound', 'Imaging test using sound waves to view organs', 120.0)
    ]

    for name, description, price in test_types:
        if not TestType.query.filter_by(test_name=name).first():
            test_type = TestType(test_name=name, description=description, price=price)
            db.session.add(test_type)
    db.session.commit()
    print("Test Types created successfully.")

def create_tests():
    patients = Patient.query.all()
    doctors = Doctor.query.all()
    test_types = TestType.query.all()
    lab_techs = LabTech.query.all()
    appointments = Appointment.query.all()

    for _ in range(5):  # Create 5 tests
        patient = random.choice(patients)
        doctor = random.choice(doctors)
        test_type = random.choice(test_types)
        lab_tech = random.choice(lab_techs)

        # Ensure that a valid appointment exists for the patient
        appointment = random.choice([a for a in appointments if a.patient_id == patient.id])

        # Ensure the doctor in the appointment matches the randomly selected doctor
        doctor_for_appointment = appointment.doctor

        # Create the test and include the appointment_id
        test = Test(
            patient_id=patient.id,
            doctor_id=doctor_for_appointment.id,  # Correctly link to the appointment's doctor
            test_types_id=test_type.id,
            lab_tech_id=lab_tech.id,
            created_at=fake.date_this_year(),
            appointment_id=appointment.id  # Link the test to the appointment
        )
        db.session.add(test)

    db.session.commit()
    print("Tests created successfully.")

def create_test_reports():
    tests = Test.query.all()
    for test in tests:
        test_report = TestReport(
            test_id=test.id,
            parameter=fake.word(),  # Example: Hemoglobin, Cholesterol, etc.
            result=fake.word(),      # Example: 12.3 g/dL, 200 mg/dL, etc.
            remark=random.choice(['Normal', 'High', 'Low', 'Critical']),  # Example remarks
            created_at=datetime.utcnow()  # Timestamp for when the report was created
        )
        db.session.add(test_report)
    db.session.commit()
    print("Test reports created successfully.")



def seed_database():
    drop_all_tables()  # First drop and recreate tables
    create_doctors()  # Now we can safely insert into the doctors table
    create_staffs()
    create_lab_techs()
    create_patients()
    create_medicines()
    create_appointments()
    create_consultations()
    create_diagnoses()
    create_prescriptions()
    create_payments()
    create_test_types()
    create_tests()
    create_test_reports()

if __name__ == '__main__':
    with app.app_context():
        seed_database()
