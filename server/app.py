from models import db, Doctor, Staff, Diagnosis, TestReport, LabTech, Patient, Payment, Consultation, Prescription, Medicine, Test, TestType, Appointment, ConsultationNotes, DiagnosisNotes
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify, abort
import requests 
from flask_restful import Api, Resource 
from flask_migrate import Migrate
from flask_cors import CORS
import base64
import os


from datetime import datetime



BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

CORS(app)

# MPESA Configuration
MPESA_CONSUMER_KEY = 'F3ryTTFGrFsyCewzqfogNQkrsce7uAV0qK5LdFAP4YFPKdpd'
MPESA_CONSUMER_SECRET = 'H83qpQELVEPIbg8dJ91nVDgsIFKs4PxOddyjcRkVVU6lJpthZTF9wtZkPHGN59r0'
MPESA_BASE_URL = 'https://sandbox.safaricom.co.ke'  # Use production URL in live environment
MPESA_SHORTCODE = '123456'  # Your MPESA shortcode
MPESA_PASSKEY = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
CALLBACK_URL = 'https://your-callback-url.com/mpesa/callback'

# Index route
class Index(Resource):
    def get(self):
        response_dict = {"message": "Afya Mis"}
        return make_response(response_dict, 200)

api.add_resource(Index, '/')

class Consultations(Resource):
    def get(self, consultation_id=None):
        if consultation_id:
            # Fetch a single consultation by ID
            consultation = Consultation.query.filter_by(id=consultation_id).first()
            
            # If no consultation is found, return a 404 error
            if not consultation:
                return make_response({"message": f"Consultation with ID {consultation_id} not found"}, 404)
            
            # Return only the specified fields 
            return make_response(consultation.to_dict(), 200)
        
        # Fetch all consultations if no consultation_id is provided
        consultations = Consultation.query.all()
        
        if not consultations:
            return make_response({"message": "No consultations found"}, 404)
        
        # Serialize the consultation data into a list of dictionaries
        consultation_data = [consultation.to_dict() for consultation in consultations]
        
        # Return the list of consultations as a JSON response
        return make_response(jsonify(consultation_data),  200)
     

    def post(self):
        # Create a new consultation
        data = request.get_json()

        # Validate input data
        if not data.get('patient_id') or not data.get('doctor_id') or not data.get('consultation_date') :
            return make_response({"message": "Missing required fields (patient_id, doctor_id, consultation_date)"}, 400)

        # Create a new Consultation object
        new_consultation = Consultation(
            patient_id=data['patient_id'],
            doctor_id=data['doctor_id'],
            consultation_date=datetime.fromisoformat(data['consultation_date']),
        )

        try:
            db.session.add(new_consultation)
            db.session.commit()
            return make_response({"message": "Consultation created", "id": new_consultation.id}, 201)
        except Exception as e:
            db.session.rollback()
            return make_response({"message": f"Error creating consultation: {str(e)}"}, 500)

    def delete(self, consultation_id):
        # Delete a consultation by ID
        consultation = Consultation.query.filter_by(id=consultation_id).first()
        
        if not consultation:
            return make_response({"message": f"Consultation with ID {consultation_id} not found"}, 404)

        try:
            db.session.delete(consultation)
            db.session.commit()
            return make_response({"message": f"Consultation with ID {consultation_id} deleted"}, 200)
        except Exception as e:
            db.session.rollback()
            return make_response({"message": f"Error deleting consultation: {str(e)}"}, 500)   

class Notes(Resource):
    def get(self, consultationNotes_id=None):
        if consultationNotes_id:
            # Fetch a single note by ID
            note = ConsultationNotes.query.filter_by(id=consultationNotes_id).first()
            if not note:
                return make_response({"message": f"Notes with ID {consultationNotes_id} not found"}, 404)
            
            # Return specified fields
            return make_response(note.to_dict(), 200)

        # Fetch all notes
        notes = ConsultationNotes.query.all()
        if not notes:
            return make_response({"message": "No notes found"}, 404)
        
        # Serialize and return all notes
        notes_data = [note.to_dict() for note in notes]
        return make_response(notes_data, 200)
    
    def post(self):
        # Create a new note
        data = request.get_json()
        print(f"Data: {data}") 
        # Validate input data
        if not data.get('notes') or not data.get('patient_id') or not data.get('consultation_id') or not data.get('created_at'):
            return make_response({"message": "Missing required fields (notes, patient_id, consultation_id, created_at)"}, 400)

        # Create a new ConsultationNotes object
        new_note = ConsultationNotes(
            notes=data['notes'],
            patient_id=data['patient_id'],
            consultation_id=data['consultation_id'],
            created_at=datetime.now(),
        )

        try:
            db.session.add(new_note)
            db.session.commit()
            return make_response({"message": "Note created", "id": new_note.id}, 201)
        except Exception as e:
            db.session.rollback()
            return make_response({"message": f"Error creating note: {str(e)}"}, 500)
        
    def delete(self, consultationNotes_id):
        #delete a note by id
        note = ConsultationNotes.query.filter_by(id=consultationNotes_id).first()
        if not note:
            return make_response({"message": f"Note with ID {consultationNotes_id} not found"}, 404)
        
        try:
            db.session.delete(note)
            db.session.commit()
            return make_response({"message": f"Note with ID {consultationNotes_id} deleted"}, 200)
        except Exception as e:
            db.session.rollback()
            return make_response({"message": f"Error deleting note: {str(e)}"}, 500)
api.add_resource(Consultations, '/consultations', '/consultations/<int:consultation_id>')  
api.add_resource(Notes, '/consultation_notes', '/consultation_notes/<int:consultationNotes_id>')

# Patients resource for CRUD operations
class Patients(Resource):
    def get(self, patient_id=None):
        if patient_id:
            patient = Patient.query.get(patient_id)
            if not patient:
                return make_response({"message": f"Patient with ID {patient_id} not found"}, 404)

            patient_data = {
                "id": patient.id,
                "name": patient.name,
                "gender": patient.gender,
                "phone_number": patient.phone_number,
                "medical_history": patient.medical_history,
                "date_of_birth": patient.date_of_birth.isoformat(),
                "address": patient.address,
                "email": patient.email
            }
            return make_response(patient_data, 200)

        patients = Patient.query.all()
        if not patients:
            return make_response({"message": "No patients found"}, 404)

        patient_data = [{
            "id": patient.id,
            "name": patient.name,
            "gender": patient.gender,
            "phone_number": patient.phone_number,
            "medical_history": patient.medical_history,
            "date_of_birth": patient.date_of_birth.isoformat(),
            "address": patient.address,
            "email": patient.email
        } for patient in patients]
        return make_response(patient_data, 200)

    def post(self):
        data = request.get_json()
        # Check for missing required fields
        required_fields = ['name', 'gender', 'phone_number', 'medical_history', 'date_of_birth', 'email']
        if not all(field in data for field in required_fields):
            return make_response({"message": "Missing required fields"}, 400)

        # Check if email or phone number already exists
        existing_patient = Patient.query.filter(
            (Patient.email == data['email']) | (Patient.phone_number == data['phone_number'])
        ).first()

        if existing_patient:
            return make_response({"message": "Patient already exists with the given email or phone number."}, 400)

        # Check if email is provided and not empty
        if not data.get('email'):
            return make_response({"message": "Email is required and cannot be empty."}, 400)

        try:
            date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return make_response({"message": "Invalid date format, should be YYYY-MM-DD"}, 400)

        patient = Patient(
            name=data['name'],
            gender=data['gender'],
            phone_number=data['phone_number'],
            medical_history=data['medical_history'],
            date_of_birth=date_of_birth,
            email=data['email']
        )
        db.session.add(patient)
        db.session.commit()
        return make_response({"message": "Patient added successfully", "id": patient.id}, 201)

    def patch(self, patient_id):
        patient = Patient.query.get(patient_id)
        if not patient:
            return make_response({"message": f"Patient with ID {patient_id} not found"}, 404)

        data = request.get_json()
        if 'name' in data:
            patient.name = data['name']
        if 'gender' in data:
            patient.gender = data['gender']
        if 'phone_number' in data:
            patient.phone_number = data['phone_number']
        if 'address' in data:
            patient.address = data['phone_number']
        if 'medical_history' in data:
            patient.medical_history = data['medical_history']
        if 'date_of_birth' in data:
            try:
                date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
                patient.date_of_birth = date_of_birth
            except ValueError:
                return make_response({"message": "Invalid date format, should be YYYY-MM-DD"}, 400)
        if 'email' in data:
            patient.email = data['email']

        db.session.commit()
        return make_response({"message": "Patient updated successfully"}, 200)

    def delete(self, patient_id):
        patient = Patient.query.get(patient_id)
        if not patient:
            return make_response({"message": f"Patient with ID {patient_id} not found"}, 404)

        db.session.delete(patient)
        db.session.commit()
        return make_response({"message": "Patient deleted successfully"}, 200)

api.add_resource(Patients, '/patients', '/patients/<int:patient_id>')

class Medicines(Resource):
    def get(self, medicine_id=None):
        if medicine_id:
            medicine = Medicine.query.get(medicine_id)
            if not medicine:
                return make_response({"message": f"Medicine with ID {medicine_id} not found"}, 404)
            
            medicine_data = {
                "id": medicine.id,
                "name": medicine.name,
                "description": medicine.description
            }
            return make_response(medicine_data, 200)
        
        medicines = Medicine.query.all()
        if not medicines:
            return make_response({"message": "No medicines found"}, 404)

        medicine_data = [{
            "id": medicine.id,
            "name": medicine.name,
            "description": medicine.description
        } for medicine in medicines]
        return make_response(medicine_data, 200)

    def post(self):
        data = request.get_json()
        # Check for missing required fields
        if not data.get('name'):
            return make_response({"message": "Name is required and cannot be empty."}, 400)

        medicine = Medicine(
            name=data['name'],
            description=data.get('description', "")
        )
        db.session.add(medicine)
        db.session.commit()
        return make_response({"message": "Medicine added successfully", "id": medicine.id}, 201)

    def patch(self, medicine_id):
        medicine = Medicine.query.get(medicine_id)
        if not medicine:
            return make_response({"message": f"Medicine with ID {medicine_id} not found"}, 404)

        data = request.get_json()
        if 'name' in data:
            medicine.name = data['name']
        if 'description' in data:
            medicine.description = data['description']

        db.session.commit()
        return make_response({"message": "Medicine updated successfully"}, 200)

    def delete(self, medicine_id):
        medicine = Medicine.query.get(medicine_id)
        if not medicine:
            return make_response({"message": f"Medicine with ID {medicine_id} not found"}, 404)

        db.session.delete(medicine)
        db.session.commit()
        return make_response({"message": "Medicine deleted successfully"}, 200)

api.add_resource(Medicines, '/medicines', '/medicines/<int:medicine_id>')





# Diagnosis Resource
class Diagnoses(Resource):
    def get(self, diagnosis_id=None):
        # Fetch a specific diagnosis by ID if provided
        if diagnosis_id:
            diagnosis = Diagnosis.query.get(diagnosis_id)
            if not diagnosis:
                return make_response({"message": f"Diagnosis with ID {diagnosis_id} not found"}, 404)
            
            # Serialize the diagnosis data
            diagnosis_data = {
                "id": diagnosis.id,
                "patient_id": diagnosis.patient_id,
                "doctor_id": diagnosis.doctor_id,
                "diagnosis_description": diagnosis.diagnosis_description,
                "created_at": diagnosis.created_at.isoformat()
            }
            
            return make_response(diagnosis_data, 200)
        
        # Fetch all diagnoses if no ID is provided
        diagnoses = Diagnosis.query.all()
        if not diagnoses:
            return make_response({"message": "No diagnoses found"}, 404)
        
        # Serialize all diagnosis data
        diagnoses_data = [{
            "id": diagnosis.id,
            "patient_id": diagnosis.patient_id,
            "doctor_id": diagnosis.doctor_id,
            "diagnosis_description": diagnosis.diagnosis_description,
            "created_at": diagnosis.created_at.isoformat()
        } for diagnosis in diagnoses]
        
        return make_response(diagnoses_data, 200)

    def post(self):
        # Extract data from the request JSON
        data = request.get_json()
        
        # Validate that required fields are present
        patient_id = data.get("patient_id")
        doctor_id = data.get("doctor_id")
        diagnosis_description = data.get("diagnosis_description")
        
        if not all([patient_id, doctor_id, diagnosis_description]):
            return make_response({"message": "Missing required fields"}, 400)
        
        # Create a new Diagnosis record
        new_diagnosis = Diagnosis(
            patient_id=patient_id,
            doctor_id=doctor_id,
            diagnosis_description=diagnosis_description,
            created_at=datetime.utcnow()
        )
        
        # Add the new record to the session and commit
        db.session.add(new_diagnosis)
        db.session.commit()
        
        # Return the created diagnosis data as a response
        response_data = {
            "id": new_diagnosis.id,
            "patient_id": new_diagnosis.patient_id,
            "doctor_id": new_diagnosis.doctor_id,
            "diagnosis_description": new_diagnosis.diagnosis_description,
            "created_at": new_diagnosis.created_at.isoformat()
        }
        
        return make_response(response_data, 201)

# Add the resource routes
api.add_resource(Diagnoses, '/diagnoses', '/diagnoses/<int:diagnosis_id>')



# DiagnosisNotes Resource
class DiagnosisNotesResource(Resource):
    def get(self, note_id=None):
        # Fetch a specific diagnosis note by ID if provided
        if note_id:
            note = DiagnosisNotes.query.get(note_id)
            if not note:
                return make_response({"message": f"Diagnosis note with ID {note_id} not found"}, 404)
            
            # Serialize the note data
            note_data = {
                "id": note.id,
                "created_at": note.created_at.isoformat() if note.created_at else None,
                "diagnosis_id": note.diagnosis_id,
                "notes": note.notes,
                "patient_id": note.patient_id
            }
            
            return make_response(note_data, 200)
        
        # Fetch all diagnosis notes if no ID is provided
        notes = DiagnosisNotes.query.all()
        if not notes:
            return make_response({"message": "No diagnosis notes found"}, 404)
        
        # Serialize all notes data
        notes_data = [{
            "id": note.id,
            "created_at": note.created_at.isoformat() if note.created_at else None,
            "diagnosis_id": note.diagnosis_id,
            "notes": note.notes,
            "patient_id": note.patient_id
        } for note in notes]
        
        return make_response(notes_data, 200)

    def post(self):
        # Extract data from the request JSON
        data = request.get_json()
        
        # Validate that required fields are present
        diagnosis_id = data.get("diagnosis_id")
        notes = data.get("notes")
        patient_id = data.get("patient_id")
        
        if not all([diagnosis_id, notes, patient_id]):
            return make_response({"message": "Missing required fields"}, 400)
        
        # Create a new DiagnosisNote record
        new_note = DiagnosisNotes(
            created_at=datetime.utcnow(),
            diagnosis_id=diagnosis_id,
            notes=notes,
            patient_id=patient_id
        )
        
        # Add the new record to the session and commit
        db.session.add(new_note)
        db.session.commit()
        
        # Return the created note data as a response
        response_data = {
            "id": new_note.id,
            "created_at": new_note.created_at.isoformat(),
            "diagnosis_id": new_note.diagnosis_id,
            "notes": new_note.notes,
            "patient_id": new_note.patient_id
        }
        
        return make_response(response_data, 201)

# Add the resource routes
api.add_resource(DiagnosisNotesResource, '/diagnosis_notes', '/diagnosis_notes/<int:note_id>')

# Doctor Resource
class DoctorsResource(Resource):
    def get(self, doctor_id=None):
        if doctor_id:
            # Fetch a specific doctor by ID if provided
            doctor = Doctor.query.get(doctor_id)
            if not doctor:
                return make_response({"message": f"Doctor with ID {doctor_id} not found"}, 404)
            
            # Serialize the doctor data
            doctor_data = {
                "id": doctor.id,
                "name": doctor.name,
                "email": doctor.email,
                "phone_number": doctor.phone_number,
                "speciality": doctor.speciality 
            }
            
            return make_response(doctor_data, 200)
        
        # Fetch all doctors if no ID is provided
        doctors = Doctor.query.all()
        if not doctors:
            return make_response({"message": "No doctors found"}, 404)
        
        # Serialize all doctor data
        doctors_data = [{
            "id": doctor.id,
            "name": doctor.name,
            "email": doctor.email,
            "phone_number": doctor.phone_number,
            "speciality": doctor.speciality 
        } for doctor in doctors]
        
        return make_response(doctors_data, 200)

    def post(self):
        # Extract data from the request JSON
        data = request.get_json()
        
        # Validate required fields
        name = data.get("name")
        email = data.get("email")
        phone_number = data.get("phone_number")
        speciality = data.get("speciality") 
        
        if not all([name, email, phone_number]):
            return make_response({"message": "Missing required fields"}, 400)
        
        # Create a new Doctor record
        new_doctor = Doctor(
            name=name,
            email=email,
            phone_number=phone_number,
            speciality=speciality 
        )
        
        # Add the new record to the session and commit
        db.session.add(new_doctor)
        db.session.commit()
        
        # Return the created doctor data as a response
        response_data = {
            "id": new_doctor.id,
            "name": new_doctor.name,
            "email": new_doctor.email,
            "phone_number": new_doctor.phone_number,
            "speciality": new_doctor.speciality 
        }
        
        return make_response(response_data, 201)

# Add the resource routes
api.add_resource(DoctorsResource, '/doctors', '/doctors/<int:doctor_id>')

class Appointments(Resource):
    def get(self):
        appointments = Appointment.query.all()
        response_dict_list = []

        for appointment in appointments:
            # Patient and Doctor data extraction (using inline conditionals to reduce repetition)
            patient = appointment.patient
            doctor = appointment.doctor

            # Format appointment date and time
            formatted_date = appointment.appointment_date.strftime("%Y-%m-%d") if appointment.appointment_date else None
            formatted_time = appointment.appointment_time.strftime("%I:%M %p") if appointment.appointment_time else None

            # Construct the response dictionary for each appointment
            response_dict = {
                "id": appointment.id,
                "appointment_date": formatted_date,
                "appointment_time": formatted_time,
                "patient": {
                    "id": patient.id if patient else None,
                    "name": patient.name if patient else None,
                    "phone_number": patient.phone_number if patient else None,
                    "gender": patient.gender if patient else None,
                    "email": patient.email if patient else None,
                },
                "doctor": {
                    "id": doctor.id if doctor else None,
                    "name": doctor.name if doctor else None,
                    "phone_number": doctor.phone_number if doctor else None,
                    "email": doctor.email if doctor else None,
                },
            }

            response_dict_list.append(response_dict)

        return make_response(jsonify(response_dict_list), 200)

    def post(self):
        data = request.get_json()

        # Validate required fields
        if not all(k in data for k in ("patient_id", "doctor_id", "appointment_date", "appointment_time")):
            return {"error": "Missing required fields"}, 400

        # Convert appointment date and time from string to datetime objects
        appointment_date = datetime.strptime(data["appointment_date"], "%Y-%m-%d").date()
        appointment_time = datetime.strptime(data["appointment_time"], "%H:%M").time()

        # Create and add the new appointment
        new_appointment = Appointment(
            patient_id=data["patient_id"],
            doctor_id=data["doctor_id"],
            appointment_date=appointment_date,
            appointment_time=appointment_time
        )

        db.session.add(new_appointment)
        db.session.commit()

        # Prepare response data
        response_data = {
            "id": new_appointment.id,
            "patient_id": new_appointment.patient_id,
            "doctor_id": new_appointment.doctor_id,
            "appointment_date": new_appointment.appointment_date.strftime("%Y-%m-%d"),
            "appointment_time": new_appointment.appointment_time.strftime("%H:%M")
        }

        return response_data, 201

api.add_resource(Appointments, '/appointments')

class AppointmentByID(Resource):
    def get(self, id):
        appointment = Appointment.query.filter_by(id=id).first()

        if appointment is None:
            return make_response(jsonify({"error": "Appointment not found"}), 404)

        # Format appointment date and time
        formatted_date = appointment.appointment_date.strftime("%Y-%m-%d") if appointment.appointment_date else None
        formatted_time = appointment.appointment_time.strftime("%I:%M %p") if appointment.appointment_time else None

        # Patient and Doctor data extraction
        patient = appointment.patient
        doctor = appointment.doctor

        # Construct the appointment response
        appointment_dict = {
            "id": appointment.id,
            "appointment_date": formatted_date,
            "appointment_time": formatted_time,
            "patient": {
                "id": patient.id if patient else None,
                "name": patient.name if patient else None,
                "phone_number": patient.phone_number if patient else None,
                "gender": patient.gender if patient else None,
                "email": patient.email if patient else None,
            },
            "doctor": {
                "id": doctor.id if doctor else None,
                "name": doctor.name if doctor else None,
                "phone_number": doctor.phone_number if doctor else None,
                "email": doctor.email if doctor else None,
            },
        }

        return make_response(jsonify(appointment_dict), 200)

    def delete(self, id):
        appointment = Appointment.query.filter_by(id=id).first()

        if appointment is None:
            return make_response(jsonify({"error": "Appointment not found"}), 404)

        # Delete the appointment from the database
        db.session.delete(appointment)
        db.session.commit()

        return make_response(jsonify({"message": f"Appointment with ID {id} has been deleted successfully."}), 200)

    def patch(self, id):
        appointment = Appointment.query.filter_by(id=id).first()

        if appointment is None:
            return make_response(jsonify({"error": "Appointment not found"}), 404)

        data = request.get_json()

        # Update fields in the appointment based on the provided data
        for key, value in data.items():
            if hasattr(appointment, key):
                if key == 'appointment_date':
                    appointment.appointment_date = datetime.strptime(value, '%Y-%m-%d').date()
                elif key == 'appointment_time':
                    appointment.appointment_time = datetime.strptime(value, '%H:%M').time()
                else:
                    setattr(appointment, key, value)

        # Commit the changes to the database
        db.session.commit()

        return make_response(jsonify({"message": f"Appointment with ID {id} has been updated successfully."}), 200)

api.add_resource(AppointmentByID, '/appointments/<int:id>')

# Prescriptions Resource
class Prescriptions(Resource):
    def get(self, prescription_id=None):
        if prescription_id:
            prescription = db.session.get(Prescription, prescription_id)
            if not prescription:
                return make_response({"message": "Prescription not found"}, 404)

            return jsonify({
                "id": prescription.id,
                "medication": prescription.medicine.name if prescription.medicine else None,
                "dosage": prescription.dosage,
                "prescription_date": prescription.prescription_date.strftime("%Y-%m-%d") if prescription.prescription_date else None,
                "quantity": prescription.quantity,
                "duration": prescription.duration,
                "patient_id": prescription.patient_id,
                "doctor_id": prescription.doctor_id,
                "appointment_id": prescription.appointment_id  # Include appointment_id
            })

        # If no `prescription_id` is provided, fetch all prescriptions
        prescriptions = Prescription.query.all()
        return make_response(jsonify([{
            "id": p.id,
            "medication": p.medicine.name if p.medicine else None,
            "dosage": p.dosage,
            "prescription_date": p.prescription_date.strftime("%Y-%m-%d") if p.prescription_date else None,
            "quantity": p.quantity,
            "duration": p.duration,
            "patient_id": p.patient_id,
            "doctor_id": p.doctor_id,
            "appointment_id": p.appointment_id  # Include appointment_id
        } for p in prescriptions]), 200)

    def post(self):
        data = request.get_json()

        # Validate required fields in a single line
        if not all(k in data for k in ("appointment_id", "patient_id", "doctor_id", "medicine_id", "dosage", "prescription_date", "quantity", "duration")):
            return {"error": "Missing required fields"}, 400

        # Convert prescription_date
        prescription_date = datetime.strptime(data["prescription_date"], "%Y-%m-%d").date()

        # Inline checks for each entity with a compact error message return
        appointment = db.session.get(Appointment, data["appointment_id"])
        if not appointment:
            return {"error": "Invalid appointment ID"}, 400

        patient = db.session.get(Patient, data["patient_id"])
        if not patient:
            return {"error": "Invalid patient ID"}, 400

        doctor = db.session.get(Doctor, data["doctor_id"])
        if not doctor:
            return {"error": "Invalid doctor ID"}, 400

        medicine = db.session.get(Medicine, data["medicine_id"])
        if not medicine:
            return {"error": "Invalid medicine ID"}, 400

        # Create the new Prescription object in a single step
        new_prescription = Prescription(
            appointment_id=data["appointment_id"],
            patient_id=data["patient_id"],
            doctor_id=data["doctor_id"],
            medicine_id=data["medicine_id"],
            dosage=data["dosage"],
            prescription_date=prescription_date,
            quantity=data["quantity"],
            duration=data["duration"]
        )

        # Add and commit the new prescription
        db.session.add(new_prescription)
        db.session.commit()

        return make_response({"message": "Prescription added", "id": new_prescription.id}, 201)

    def delete(self, prescription_id):
        prescription = db.session.get(Prescription, prescription_id)
        if not prescription:
            return make_response({"message": "Prescription not found"}, 404)

        db.session.delete(prescription)
        db.session.commit()
        return make_response({"message": "Prescription deleted"}, 200)

# Add Prescriptions resource to the API
api.add_resource(Prescriptions, '/prescriptions', '/prescriptions/<int:prescription_id>')

# routes for test and test type
@app.route('/test-types', methods=['GET'])
def get_test_types():
    test_types = TestType.query.all()
    return jsonify([test_type.to_dict() for test_type in test_types])

@app.route('/test-types/<int:id>', methods=['GET'])
def get_test_type(id):
    test_type = TestType.query.get(id)
    if test_type is None:
        abort(404, description="TestType not found")
    return jsonify(test_type.to_dict())

@app.route('/test-types', methods=['POST'])
def create_test_type():
    data = request.get_json()
    if not data or not data.get('test_name') or not data.get('description') or not data.get('price'):
        abort(400, description="Missing required fields")
    
    test_type = TestType(
        test_name=data['test_name'],
        description=data['description'],
        price=data['price']
    )
    db.session.add(test_type)
    db.session.commit()
    return jsonify(test_type.to_dict()), 201

@app.route('/test-types/<int:id>', methods=['PATCH'])
def update_test_type(id):
    test_type = TestType.query.get(id)
    if test_type is None:
        abort(404, description="TestType not found")
    
    data = request.get_json()
    test_type.test_name = data.get('test_name', test_type.test_name)
    test_type.description = data.get('description', test_type.description)
    test_type.price = data.get('price', test_type.price)
    
    db.session.commit()
    return jsonify(test_type.to_dict())

@app.route('/test-types/<int:id>', methods=['DELETE'])
def delete_test_type(id):
    test_type = TestType.query.get(id)
    if test_type is None:
        abort(404, description="TestType not found")
    
    db.session.delete(test_type)
    db.session.commit()
    return jsonify({"message": "TestType deleted successfully"}), 200

@app.route('/tests', methods=['GET'])
def get_tests():
    tests = Test.query.all()
    return jsonify([test.to_dict() for test in tests])

@app.route('/tests/<int:id>', methods=['GET'])
def get_test(id):
    test = Test.query.get(id)
    if test is None:
        abort(404, description="Test not found")
    return jsonify(test.to_dict())

@app.route('/tests', methods=['POST'])
def create_test():
    # Get the data from the request
    data = request.get_json()

    # Validate required fields
    required_fields = ['created_at', 'status', 'patient', 'doctor', 'lab_tech', 'test_types']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400

    # Parse the created_at field
    try:
        created_at = datetime.strptime(data['created_at'], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({'message': 'Invalid date format. Please use YYYY-MM-DD HH:MM:SS.'}), 400

    # Validate the status field
    if data['status'] not in ['pending', 'completed']:
        return jsonify({'message': 'Invalid status. Allowed values are "pending" and "completed".'}), 400

    # Find related objects (patient, doctor, lab tech, test_type) by name
    patient = Patient.query.filter_by(name=data['patient']['name']).first()
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    doctor = Doctor.query.filter_by(name=data['doctor']['name']).first()
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    lab_tech = LabTech.query.filter_by(name=data['lab_tech']['name']).first()
    if not lab_tech:
        return jsonify({'message': 'Lab Tech not found'}), 404

    test_type = TestType.query.filter_by(test_name=data['test_types']['test_name']).first()
    if not test_type:
        return jsonify({'message': 'Test Type not found'}), 404

    # Create a new Test record
    new_test = Test(
        patient_id=patient.id,  # Now using patient_id correctly
        doctor_id=doctor.id,
        lab_tech_id=lab_tech.id,
        test_types_id=test_type.id,
        status=data['status'],
        # test_results=data.get('test_results', ''),  # Optional: handle missing test results
        created_at=created_at
    )

    # Add to the session and commit to the database
    db.session.add(new_test)
    db.session.commit()

    # Return the created test data
    return jsonify({
        'id': new_test.id,
        'created_at': new_test.created_at,
        'status': new_test.status,
        'patient': {'name': new_test.patient.name},
        'doctor': {'name': new_test.doctor.name},
        'lab_tech': {'name': new_test.lab_tech.name},
        'test_types': {'test_name': new_test.test_types.test_name}
    }), 201

@app.route('/tests/<int:test_id>', methods=['PATCH'])
def update_test(test_id):
    # Get the data from the request
    data = request.get_json()

    # Find the test by ID
    test = Test.query.get(test_id)
    if not test:
        return jsonify({'message': 'Test not found'}), 404

    # Only update the status if provided in the request data
    if 'status' in data:
        if data['status'] not in ['pending', 'completed']:
            return jsonify({'message': 'Invalid status. Allowed values are "pending" and "completed".'}), 400
        test.status = data['status']

    # Commit the changes to the database
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating status: {str(e)}'}), 500

    # Return the updated test data
    return jsonify({
        'id': test.id,
        'created_at': test.created_at,
        'status': test.status,
        'test_results': test.test_results,
        'patient': {'name': test.patient.name},
        'doctor': {'name': test.doctor.name},
        'lab_tech': {'name': test.lab_tech.name},
        'test_types': {'test_name': test.test_types.test_name}
    }), 200

@app.route('/tests/<int:test_id>', methods=['DELETE'])
def delete_test(test_id):
    # Find the test by ID
    test = Test.query.get(test_id)
    if not test:
        return jsonify({'message': 'Test not found'}), 404

    # Delete the test from the database
    db.session.delete(test)
    db.session.commit()

    # Return a confirmation message
    return jsonify({'message': 'Test deleted successfully'}), 200

# routes for staff
@app.route('/staffs', methods=['GET'])
def get_staff():
    staff_members = Staff.query.all()
    return jsonify([{
        'id': staff.id,
        'name': staff.name,
        'email': staff.email,
        'phone_number': staff.phone_number,
        'role': staff.role
    } for staff in staff_members]), 200


@app.route('/staffs/<int:staff_id>', methods=['GET'])
def get_staff_by_id(staff_id):
    staff = Staff.query.get(staff_id)
    if not staff:
        return jsonify({'message': 'Staff member not found'}), 404

    return jsonify({
        'id': staff.id,
        'name': staff.name,
        'email': staff.email,
        'phone_number': staff.phone_number,
        'role': staff.role
    }), 200

@app.route('/staffs', methods=['POST'])
def create_staff():
    data = request.get_json()

    # Validate required fields
    required_fields = ['name', 'email', 'phone_number', 'role']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400

    # Check for unique constraints (email and phone number)
    if Staff.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400

    if Staff.query.filter_by(phone_number=data['phone_number']).first():
        return jsonify({'message': 'Phone number already exists'}), 400

    # Create the staff member
    new_staff = Staff(
        name=data['name'],
        email=data['email'],
        phone_number=data['phone_number'],
        role=data['role']
    )

    db.session.add(new_staff)
    db.session.commit()

    return jsonify({
        'id': new_staff.id,
        'name': new_staff.name,
        'email': new_staff.email,
        'phone_number': new_staff.phone_number,
        'role': new_staff.role
    }), 201

@app.route('/staffs/<int:staff_id>', methods=['PATCH'])
def update_staff(staff_id):
    data = request.get_json()

    # Find the staff member
    staff = Staff.query.get(staff_id)
    if not staff:
        return jsonify({'message': 'Staff member not found'}), 404

    # Update fields if they are provided
    if 'name' in data:
        staff.name = data['name']
    if 'email' in data:
        if Staff.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already exists'}), 400
        staff.email = data['email']
    if 'phone_number' in data:
        if Staff.query.filter_by(phone_number=data['phone_number']).first():
            return jsonify({'message': 'Phone number already exists'}), 400
        staff.phone_number = data['phone_number']
    if 'role' in data:
        staff.role = data['role']

    # Commit the changes
    db.session.commit()

    return jsonify({
        'id': staff.id,
        'name': staff.name,
        'email': staff.email,
        'phone_number': staff.phone_number,
        'role': staff.role
    }), 200

@app.route('/staffs/<int:staff_id>', methods=['DELETE'])
def delete_staff(staff_id):
    # Find the staff member
    staff = Staff.query.get(staff_id)
    if not staff:
        return jsonify({'message': 'Staff member not found'}), 404

    # Delete the staff member
    db.session.delete(staff)
    db.session.commit()

    return jsonify({'message': 'Staff member deleted successfully'}), 200

@app.route('/lab_techs', methods=['GET'])
def get_lab_techs():
    lab_techs = LabTech.query.all()
    return jsonify([{
        'id': lab_tech.id,
        'name': lab_tech.name,
        'email': lab_tech.email,
        'phone_number': lab_tech.phone_number
    } for lab_tech in lab_techs]), 200


@app.route('/lab_techs/<int:lab_tech_id>', methods=['GET'])
def get_lab_tech_by_id(lab_tech_id):
    lab_tech = LabTech.query.get(lab_tech_id)
    if not lab_tech:
        return jsonify({'message': 'Lab Technician not found'}), 404

    return jsonify({
        'id': lab_tech.id,
        'name': lab_tech.name,
        'email': lab_tech.email,
        'phone_number': lab_tech.phone_number
    }), 200

@app.route('/lab_techs', methods=['POST'])
def create_lab_tech():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'email', 'phone_number']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400

    # Check if the email and phone number already exist
    if LabTech.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400

    if LabTech.query.filter_by(phone_number=data['phone_number']).first():
        return jsonify({'message': 'Phone number already exists'}), 400

    # Create the new lab tech
    new_lab_tech = LabTech(
        name=data['name'],
        email=data['email'],
        phone_number=data['phone_number']
    )

    db.session.add(new_lab_tech)
    db.session.commit()

    return jsonify({
        'id': new_lab_tech.id,
        'name': new_lab_tech.name,
        'phone_number': new_lab_tech.phone_number,
        'email': new_lab_tech.email
    }), 201

@app.route('/lab_techs/<int:id>', methods=['PATCH'])
def update_lab_tech(id):
    data = request.get_json()

    # Find the lab tech by ID
    lab_tech = LabTech.query.get(id)
    if not lab_tech:
        return jsonify({'message': 'Lab Tech not found'}), 404

    # Update fields if they exist in the request data
    if 'name' in data:
        lab_tech.name = data['name']
    if 'email' in data:
        # Check if the new email is already used
        if LabTech.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already exists'}), 400
        lab_tech.email = data['email']
    if 'phone_number' in data:
        # Check if the new phone number is already used
        if LabTech.query.filter_by(phone_number=data['phone_number']).first():
            return jsonify({'message': 'Phone number already exists'}), 400
        lab_tech.phone_number = data['phone_number']

    # Commit the changes to the database
    db.session.commit()

    # Return the updated lab tech data
    return jsonify({
        'id': lab_tech.id,
        'name': lab_tech.name,
        'email': lab_tech.email,
        'phone_number': lab_tech.phone_number
    }), 200

@app.route('/lab_techs/<int:id>', methods=['DELETE'])
def delete_lab_tech(id):
    # Find the lab tech by ID
    lab_tech = LabTech.query.get(id)
    if not lab_tech:
        return jsonify({'message': 'Lab Tech not found'}), 404

    # Delete the lab tech
    db.session.delete(lab_tech)
    db.session.commit()

    # Return a success message
    return jsonify({'message': 'Lab Tech deleted successfully'}), 200

@app.route('/test_reports', methods=['GET'])
def get_test_reports():
    test_id = request.args.get('test_id')  # Optional filter by test_id

    # Fetch reports with related data eagerly loaded
    if test_id:
        test_reports = TestReport.query.filter_by(test_id=test_id).all()
    else:
        test_reports = TestReport.query.all()

    # Include related data in the serialized output
    results = []
    for report in test_reports:
        test = report.test  # Related test object
        results.append({
            "id": report.id,
            "parameter": report.parameter,
            "result": report.result,
            "remark": report.remark,
            "created_at": report.created_at,
            "patient_name": test.patient.name,
            "doctor_name": test.doctor.name,
            "lab_tech_name": test.lab_tech.name,
            "test_type_name": test.test_types.test_name,
        })

    return jsonify(results), 200

from datetime import datetime

@app.route('/test_reports', methods=['POST'])
def create_test_report():
    # Get JSON data from the request
    data = request.get_json()

    # Validate that the 'findings' field is provided and that each entry has 'parameter' and 'result'
    if 'findings' not in data or not all('parameter' in f and 'result' in f for f in data['findings']):
        return jsonify({"error": "Missing required fields: parameter or result in findings"}), 400

    # Validate that patient_name, doctor_name, and test_type are present
    if not all(key in data for key in ['patient_name', 'doctor_name', 'test_type']):
        return jsonify({"error": "Missing required fields: patient_name, doctor_name, or test_type"}), 400

    # Use patient_name, doctor_name, and test_type to find the related test
    test = Test.query.join(Patient).join(Doctor).join(TestType).filter(
        Patient.name == data['patient_name'],
        Doctor.name == data['doctor_name'],
        TestType.test_name == data['test_type']
    ).first()

    if not test:
        return jsonify({"error": "Test not found with the provided details"}), 400

    # Get the current datetime for 'created_at'
    created_at = datetime.utcnow()

    # Loop through each finding and insert it as a separate row in the TestReport table
    for finding in data['findings']:
        # Create a new test report entry
        test_report = TestReport(
            test_id=test.id,  # The ID of the found test
            parameter=finding['parameter'],  # Single parameter
            result=finding['result'],  # Single result
            remark=data.get('remark'),  # Optional remark (if provided)
            created_at=created_at  # Automatically set 'created_at'
        )
        
        # Add the test report to the session
        db.session.add(test_report)

    # Commit the transaction to insert all findings
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    # Construct and send the response
    response = {
        "status": "success",
        "message": "Test report created successfully",
    }

    return jsonify(response), 201

@app.route('/payments', methods=['GET'])
def get_payments():
    payments = Payment.query.join(Patient).all()
    results = [
        {
            "id": payment.id,
            "patient_name": payment.patient.name,  # Access patient's name
            "service": payment.service,
            "amount": float(payment.amount),  # Convert Decimal to float
            "payment_method": payment.payment_method,
        }
        for payment in payments
    ]
    return jsonify(results), 200

@app.route('/payments/<int:payment_id>', methods=['GET'])
def get_payment_by_id(payment_id):
    # Query the database for the payment with the given ID
    payment = Payment.query.get(payment_id)
    
    # Check if the payment exists
    if not payment:
        return jsonify({"error": "Payment not found"}), 404

    # Return the payment details including the patient's name
    result = {
        "id": payment.id,
        "patient_name": payment.patient.name,  # Access the patient's name
        "service": payment.service,
        "amount": float(payment.amount),  # Convert Decimal to float
        "payment_method": payment.payment_method,
    }

    return jsonify(result), 200

@app.route('/payments', methods=['POST'])
def add_payment():
    data = request.get_json()

    # Extract required fields
    patient_id = data.get('patient_id')
    service = data.get('service')
    amount = data.get('amount')
    payment_method = data.get('payment_method')  # 'cash' or 'mpesa'


    if payment_method not in ['cash', 'mpesa']:
        return jsonify({"error": "Invalid payment method"}), 400

    # Verify patient exists
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    # Create the payment
    payment = Payment(
        patient_id=patient_id,
        service=service,
        amount=amount,
        payment_method=payment_method
    )
    db.session.add(payment)
    db.session.commit()

    return jsonify({
        "message": "Payment added successfully",
        "payment": {
            "id": payment.id,
            "patient_name": patient.name,  # Include patient's name for convenience
            "service": payment.service,
            "amount": float(payment.amount),
            "payment_method": payment.payment_method
        }
    }), 201

# Helper Functions
def get_mpesa_access_token():
    try:
        print("Generating MPESA access token...")
        url = f"{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(url, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET))
        print(f"MPESA Token Response: {response.text}")
        response.raise_for_status()
        return response.json().get('access_token')
    except Exception as e:
        print(f"Error generating MPESA token: {e}")
        raise

def trigger_mpesa_stk_push(phone_number, amount, reference, description):
    """Initiate MPESA STK Push."""
    try:
        access_token = get_mpesa_access_token()  # Make sure you are getting the correct access token
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')  # Generate the timestamp
        password = base64.b64encode(
            (MPESA_SHORTCODE + MPESA_PASSKEY + timestamp).encode('utf-8')
        ).decode('utf-8')
        password = password.hex()  # Encode password as base64

        url = f"{MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            {    
            "BusinessShortCode": "174379",    
            "Password": "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMTYwMjE2MTY1NjI3",    
            "Timestamp":"20160216165627",    
            "TransactionType": "CustomerPayBillOnline",    
            "Amount": "1",    
            "phone_number":"phone_number",    
            "PartyB":"174379",    
            "phone_number":"phone_number",    
            "CallBackURL": "https://mydomain.com/path",    
            "AccountReference":"Test",    
            "TransactionDesc":"Test"
            }
        }
        response = requests.post(url, json=payload, headers=headers)
        print(f"MPESA Response: {response.text}")  # Log the full response
        if response.status_code == 200:
            return response.json()
        else:
            # Log error response from MPESA
            print(f"Failed MPESA request: {response.text}")
            return {"status": "error", "message": response.text}
    except Exception as e:
        print(f"Error in MPESA request: {str(e)}")
        return {"status": "error", "message": str(e)}


# Routes
@app.route('/payments/mpesa', methods=['POST'])
def mpesa_stk_push():
    data = request.get_json()

    # Log incoming data for debugging
    print("Received data for MPESA payment:", data)

    # Extract required fields
    phone_number = data.get('phone_number')
    amount = data.get('amount')
    service = data.get('service')

    # Validate required fields
    if not phone_number or not amount or not service:
        return jsonify({"error": "Missing required fields"}), 400

    # Look up the patient based on the phone number
    patient = Patient.query.filter_by(phone_number=phone_number).first()
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    # Trigger MPESA STK Push
    try:
        stk_response = trigger_mpesa_stk_push(
            phone_number=phone_number,
            amount=amount,
            reference=service,
            description=f"Payment for {service}"
        )

        if stk_response.get('ResponseCode') == '0':  # Success
            # Record the payment in the database
            payment = Payment(
                patient_id=patient.id,  # Use the patient ID from the lookup
                service=service,
                amount=amount,
                payment_method='mpesa'
            )
            db.session.add(payment)
            db.session.commit()

            return jsonify({
                "message": "MPESA STK Push initiated successfully",
                "payment": {
                    "id": payment.id,
                    "patient_name": patient.name,
                    "service": payment.service,
                    "amount": float(payment.amount),
                    "payment_method": payment.payment_method
                },
                "stk_response": stk_response
            }), 200
        else:
            return jsonify({"error": "Failed to initiate MPESA STK Push", "details": stk_response}), 400

    except Exception as e:
        return jsonify({"error": "An error occurred while processing the MPESA request", "details": str(e)}), 500



if __name__ == '__main__':
    app.run(port=5555, debug=True)
