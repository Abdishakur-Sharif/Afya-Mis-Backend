from app import app, db
from models import  Doctor, Staff, LabTech, Patient, Appointment, Test, Consultation, ConsultationNotes, DiagnosisNotes, Diagnosis, Prescription, Payment, TestType, Medicine

# Import random, Faker, datetime, and timedelta
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

# Helper function to drop all tables (clear the database)
def drop_all_tables():
    with app.app_context():
        db.drop_all()  # Drops all tables in the database
        print("All tables dropped successfully.")



# Helper function to create doctors
def create_doctors():
    for i in range(10):  # Create 10 doctors
        doctor = Doctor(
            name=fake.name(),
            email=fake.email(),
            phone_number=fake.phone_number(),
        )
        db.session.add(doctor)
    db.session.commit()
    print("Doctors created successfully.")

def create_staff():
    for i in range(10):  # Create 10 staff members
        staff = Staff(
            name=fake.name(),
            email=fake.email(),
            phone_number=fake.phone_number(),
            role=fake.job()
        )
        db.session.add(staff)
    db.session.commit()
    print("Staff created successfully.")



# Helper function to create lab techs
def create_lab_techs():
    for i in range(5):  # Create 5 lab techs
        lab_tech = LabTech(
            name=fake.name(),
            email=fake.email(),
            phone_number=fake.phone_number(),
            )
        db.session.add(lab_tech)
    db.session.commit()
    print("LabTechs created successfully.")

# Helper function to create patients
from datetime import datetime
import random

def create_patients():
    conditions = [
        'Hypertension', 'Diabetes', 'Asthma', 'Chronic Back Pain', 'Migraine', 'Anemia', 'Arthritis', 'Allergies'
    ]
    
    # Create 20 patients
    for i in range(20):
        # Create a new patient
        patient = Patient(
            name=fake.name(),
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=80),
            phone_number=fake.phone_number(),
            email=fake.email(),
            address=fake.address(),
            gender=random.choice(['Male', 'Female']),
            medical_history=random.choice(conditions)
        )
        
        # Add the patient to the session and commit to get the patient ID
        db.session.add(patient)
        db.session.commit()  # Ensure the patient is committed to the DB before continuing

        # Now the patient has a valid ID, so create the associated records
        # Create a consultation for this patient
        consultation = Consultation(
            patient_id=patient.id,  # Use the committed patient ID
            doctor_id=random.choice([doctor.id for doctor in Doctor.query.all()]),  # Randomly pick a doctor
            consultation_date=fake.date_this_year()
        )
        
        # Add consultation to the session and commit to get consultation_id
        db.session.add(consultation)
        db.session.commit()  # Ensure the consultation has a valid ID
        
        # Create consultation notes for this consultation
        consultation_notes = ConsultationNotes(
            patient_id=patient.id,  # Use the patient ID
            notes=fake.text(),
            consultation_id=consultation.id,  # Use the consultation ID
            created_at=datetime.utcnow()
        )
        db.session.add(consultation_notes)
        db.session.commit()

        # Create diagnosis for the patient
        diagnosis = Diagnosis(
            patient_id=patient.id,  # Use the patient ID
            doctor_id=random.choice([doctor.id for doctor in Doctor.query.all()]),  # Randomly pick a doctor
            created_at=datetime.utcnow()
        )
        db.session.add(diagnosis)
        db.session.commit()

        # Create diagnosis notes for the diagnosis
        diagnosis_notes = DiagnosisNotes(
            patient_id=patient.id,  # Use the patient ID
            notes=fake.text(),
            diagnosis_id=diagnosis.id,  # Use the diagnosis ID
            created_at=datetime.utcnow()
        )
        
        db.session.add(diagnosis_notes)
        db.session.commit()
    
    print("Patients and associated data created successfully.")

# Helper function to create medicines
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
        existing_medicine = Medicine.query.filter_by(name=name).first()
        if not existing_medicine:
            medicine = Medicine(
                name=name,
                description=description
            )
            db.session.add(medicine)
    db.session.commit()
    print("Medicines created successfully.")

# Helper function to create appointments
# Helper function to create appointments
def create_appointments():
    # Delete all existing appointments before creating new ones
    Appointment.query.delete()  # This removes all existing appointment data

    patients = Patient.query.all()
    doctors = Doctor.query.all()

    for i in range(5):  # Create 5 appointments
        appointment_date = fake.date_this_year()  # Generate the date once

        appointment = Appointment(
            patient_id=random.choice(patients).id,
            doctor_id=random.choice(doctors).id,
            appointment_date=appointment_date,  # Use the same date for both
            appointment_time=appointment_date,  # Ensure time and date match
        )
        db.session.add(appointment)
    
    db.session.commit()
    print("5 Appointments created successfully.")
# Helper function to create consultations

def create_consultations():
    patients = Patient.query.all()
    doctors = Doctor.query.all()

    consultation_notes = [
        "Patient presents with a headache and dizziness. Recommended further tests.",
        "Patient shows signs of chronic back pain. Suggested physical therapy.",
        "Patient reports feeling fatigued. Blood tests suggested for anemia.",
        "Patient complains of joint pain and swelling. Arthritis suspected, medication prescribed.",
        "Patient has a persistent cough. Possible asthma attack. Medication prescribed."
    ]

    for i in range(5):  # Create 5 consultations
        patient = random.choice(patients)
        doctor = random.choice(doctors)
        
        # Create the consultation object
        consultation = Consultation(
            patient_id=patient.id,
            doctor_id=doctor.id,
            consultation_date=fake.date_this_year()
        )
        db.session.add(consultation)
        db.session.commit()  # Commit so we have a valid consultation.id

        # Now, create consultation notes for the consultation
        consultation_notes_object = ConsultationNotes(
            consultation_id=consultation.id,  # Link to the consultation
            notes=random.choice(consultation_notes),  # Randomly pick a note from the list
            created_at=datetime.utcnow(),
            patient_id=patient.id
        )
        db.session.add(consultation_notes_object)
        db.session.commit()  # Commit the consultation notes

    db.session.commit()
    print("Consultations created successfully.")


# Helper function to create diagnoses
def create_diagnoses():
    conditions = [
        'Hypertension', 'Diabetes', 'Asthma', 'Chronic Back Pain', 'Migraine', 'Anemia', 'Arthritis', 'Allergies'
    ]
    patients = Patient.query.all()
    doctors = Doctor.query.all()

    for i in range(5):  # Create 5 diagnoses
        patient = random.choice(patients)
        doctor = random.choice(doctors)
        
        # Create the diagnosis object
        diagnosis = Diagnosis(
            patient_id=patient.id,
            doctor_id=doctor.id,
            diagnosis_description=random.choice(conditions),
            created_at=fake.date_this_year()
        )
        db.session.add(diagnosis)
        db.session.commit()  # Commit so we have a valid diagnosis.id

        # Now, create diagnosis notes for the diagnosis
        diagnosis_notes = DiagnosisNotes(
            diagnosis_id=diagnosis.id,  # Link to the diagnosis
            notes=fake.text(),  # Randomly generated notes for the diagnosis
            created_at=datetime.utcnow(),
            patient_id=patient.id
        )
        db.session.add(diagnosis_notes)
        db.session.commit()  # Commit the diagnosis notes

    db.session.commit()
    print("Diagnoses created successfully.")


# Helper function to create prescriptions
def create_prescriptions():
    medicines = Medicine.query.all()
    appointments = Appointment.query.all()
    patients = Patient.query.all()
    doctors = Doctor.query.all()

    for i in range(5):  # Create 5 prescriptions
        prescription = Prescription(
            appointment_id=random.choice(appointments).id,
            patient_id=random.choice(patients).id,
            doctor_id=random.choice(doctors).id,
            medicine_id=random.choice(medicines).id,
            dosage=fake.word(),
            quantity=random.randint(1, 5),
            duration=random.randint(1, 10),
            prescription_date=fake.date_this_year()
        )
        db.session.add(prescription)
    db.session.commit()
    print("Prescriptions created successfully.")

# Helper function to create payments
def create_payments():
    patients = Patient.query.all()

    for i in range(5):  # Create 5 payments
        payment = Payment(
            patient_id=random.choice(patients).id,
            service=random.choice(['Consultation', 'Lab Test', 'X-Ray', 'Blood Test']),
            amount=random.randint(100, 500)
        )
        db.session.add(payment)
    db.session.commit()
    print("Payments created successfully.")

def create_test_types():
    test_types_data = [
        ('Blood Test', 'Test to check various blood parameters', 50.0),
        ('X-Ray', 'Imaging test to examine bones and tissues', 100.0),
        ('MRI Scan', 'Magnetic resonance imaging for detailed body scans', 200.0),
        ('CT Scan', 'Computed tomography scan for internal imaging', 150.0),
        ('Urine Test', 'Test to detect infections or kidney issues', 30.0),
        ('ECG', 'Test to check the electrical activity of the heart', 75.0),
        ('Ultrasound', 'Imaging test using sound waves to view organs', 120.0)
    ]

    for test_name, description, price in test_types_data:
        existing_test_type = TestType.query.filter_by(test_name=test_name).first()
        if not existing_test_type:
            test_type = TestType(
                test_name=test_name,
                description=description,
                price=price
            )
            db.session.add(test_type)
    db.session.commit()
    print("Test Types created successfully.")

def create_tests():
    patients = Patient.query.all()
    doctors = Doctor.query.all()
    lab_techs = LabTech.query.all()
    test_types = TestType.query.all()

    statuses = ['pending', 'completed']

    for i in range(10):  # Create 10 test records
        test = Test(
            patient_id=random.choice(patients).id,
            doctor_id=random.choice(doctors).id,
            lab_tech_id=random.choice(lab_techs).id,
            test_types_id=random.choice(test_types).id,
            status=random.choice(statuses),
            test_results=fake.text(max_nb_chars=100),  # Random test results for demonstration
            created_at=fake.date_this_year()
        )
        db.session.add(test)
    db.session.commit()
    print("Tests created successfully.")


# Main function to seed the database
def seed_data():
    drop_all_tables()  # Drop all tables before reseeding
    db.create_all()    # Recreate all tables
    create_doctors()
    create_lab_techs()
    create_patients()
    create_medicines()  # New function to add medicines
    create_appointments()
    create_consultations()
    create_diagnoses()
    create_prescriptions()
    create_payments()
    create_test_types()
    create_tests()

if __name__ == "__main__":
    with app.app_context():
        seed_data()
