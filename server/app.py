from models import db, Doctor, Staff, Diagnosis, TestReport,  LabTech, Patient, Payment, Consultation, Prescription, Medicine, Test, TestType, Appointment, ConsultationNotes, DiagnosisNotes
from flask_migrate import Migrate
from flask import Flask, request , make_response, jsonify, abort
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask_cors import CORS 
import os
import base64

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


# Index route
class Index(Resource):
    def get(self):
        response_dict = {"message": "Afya Mis"}
        return make_response(response_dict, 200)

api.add_resource(Index, '/')

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

    def delete(self, doctor_id):
        # Fetch the doctor to delete by ID
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return make_response({"message": f"Doctor with ID {doctor_id} not found"}, 404)
        
        # Delete the doctor
        db.session.delete(doctor)
        db.session.commit()

        return make_response({"message": f"Doctor with ID {doctor_id} has been deleted."}, 200)
        
# Add the resource routes
api.add_resource(DoctorsResource, '/doctors', '/doctors/<int:doctor_id>')


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
                "created_at": diagnosis.created_at.isoformat(),
                "diagnosis_date": diagnosis.diagnosis_date.isoformat()
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
            "created_at": diagnosis.created_at.isoformat(),
            "diagnosis_date": diagnosis.diagnosis_date.isoformat()
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
            # diagnosis_date=datetime.utcnow(),
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
            "created_at": new_diagnosis.created_at.isoformat(),
            
        }
        
        return make_response(response_data, 201)

    def patch(self, diagnosis_id):
        diagnosis = Diagnosis.query.get(diagnosis_id)
        if not diagnosis:
            return make_response({"message": f"Diagnosis with ID {diagnosis_id} not found"}, 404)

        data = request.get_json()
        if 'diagnosis_description' in data:
            diagnosis.diagnosis_description = data['diagnosis_description']
        if 'doctor_id' in data:
            diagnosis.doctor_id = data['doctor_id']
        if 'patient_id' in data:
            diagnosis.patient_id = data['patient_id']

        db.session.commit()
        return make_response({"message": "Diagnosis updated successfully"}, 200)

    def delete(self, diagnosis_id):
        diagnosis = Diagnosis.query.get(diagnosis_id)
        if not diagnosis:
            return make_response({"message": f"Diagnosis with ID {diagnosis_id} not found"}, 404)

        db.session.delete(diagnosis)
        db.session.commit()
        return make_response({"message": "Diagnosis deleted successfully"}, 200)

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
                "created_at": note.created_at .isoformat(),
                "diagnosis_id": note.diagnosis_id,
                "note": note.note
            }
            return make_response(note_data, 200)
        
        # Fetch all diagnosis notes if no ID is provided
        notes = DiagnosisNotes.query.all()
        if not notes:
            return make_response({"message": "No diagnosis notes found"}, 404)
        
        # Serialize all note data
        notes_data = [{
            "id": note.id,
            "created_at": note.created_at.isoformat(),
            "diagnosis_id": note.diagnosis_id,
            "note": note.note
        } for note in notes]
        
        return make_response(notes_data, 200)

    def post(self):
        # Extract data from the request JSON
        data = request.get_json()
        
        # Validate that required fields are present
        diagnosis_id = data.get("diagnosis_id")
        note = data.get("note")
        
        if not all([diagnosis_id, note]):
            return make_response({"message": "Missing required fields"}, 400)
        
        # Create a new DiagnosisNote record
        new_note = DiagnosisNotes(
            diagnosis_id=diagnosis_id,
            note=note,
            created_at=datetime.utcnow()
        )
        
        # Add the new record to the session and commit
        db.session.add(new_note)
        db.session.commit()
        
        # Return the created note data as a response
        response_data = {
            "id": new_note.id,
            "diagnosis_id": new_note.diagnosis_id,
            "note": new_note.note,
            "created_at": new_note.created_at.isoformat()
        }
        
        return make_response(response_data, 201)

    def patch(self, note_id):
        note = DiagnosisNotes.query.get(note_id)
        if not note:
            return make_response({"message": f"Diagnosis note with ID {note_id} not found"}, 404)

        data = request.get_json()
        if 'note' in data:
            note.note = data['note']

        db.session.commit()
        return make_response({"message": "Diagnosis note updated successfully"}, 200)

    def delete(self, note_id):
        note = DiagnosisNotes.query.get(note_id)
        if not note:
            return make_response({"message": f"Diagnosis note with ID {note_id} not found"}, 404)

        db.session.delete(note)
        db.session.commit()
        return make_response({"message": "Diagnosis note deleted successfully"}, 200)

# Add the resource routes
api.add_resource(DiagnosisNotesResource, '/diagnosis_notes', '/diagnosis_notes/<int:note_id>')
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
        test_results=data.get('test_results', ''),  # Optional: handle missing test results
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

    # Update fields if provided in the request
    if 'status' in data:
        if data['status'] not in ['pending', 'completed']:
            return jsonify({'message': 'Invalid status. Allowed values are "pending" and "completed".'}), 400
        test.status = data['status']

    if 'test_results' in data:
        test.test_results = data['test_results']

    # Update related objects if provided
    if 'doctor' in data:
        doctor = Doctor.query.filter_by(name=data['doctor']['name']).first()
        if not doctor:
            return jsonify({'message': 'Doctor not found'}), 404
        test.doctor_id = doctor.id

    if 'lab_tech' in data:
        lab_tech = LabTech.query.filter_by(name=data['lab_tech']['name']).first()
        if not lab_tech:
            return jsonify({'message': 'Lab Tech not found'}), 404
        test.lab_tech_id = lab_tech.id

    if 'test_types' in data:
        test_type = TestType.query.filter_by(test_name=data['test_types']['test_name']).first()
        if not test_type:
            return jsonify({'message': 'Test Type not found'}), 404
        test.test_types_id = test_type.id

    # Commit the changes to the database
    db.session.commit()

    # Return the updated test data (without appointment_id)
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
    staff = Staff.query.get(staff_id)
    if not staff:
        return jsonify({'message': 'Staff member not found'}), 404

    db.session.delete(staff)
    db.session.commit()
    return jsonify({'message': 'Staff member deleted successfully'}), 200


# Routes for Lab Technician Management
@app.route('/lab_techs', methods=['GET'])
def get_lab_techs():
    lab_techs = LabTech.query.all()
    return jsonify([
        {'id': lab_tech.id, 'name': lab_tech.name, 'email': lab_tech.email, 'phone_number': lab_tech.phone_number}
        for lab_tech in lab_techs
    ]), 200


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
    required_fields = ['name', 'email', 'phone_number']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400

    if LabTech.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400

    if LabTech.query.filter_by(phone_number=data['phone_number']).first():
        return jsonify({'message': 'Phone number already exists'}), 400

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
        'email': new_lab_tech.email,
        'phone_number': new_lab_tech.phone_number
    }), 201


@app.route('/lab_techs/<int:id>', methods=['PATCH'])
def update_lab_tech(id):
    data = request.get_json()
    lab_tech = LabTech.query.get(id)
    if not lab_tech:
        return jsonify({'message': 'Lab Tech not found'}), 404

    if 'name' in data:
        lab_tech.name = data['name']
    if 'email' in data and LabTech.query.filter_by(email=data['email']).first() is None:
        lab_tech.email = data['email']
    if 'phone_number' in data and LabTech.query.filter_by(phone_number=data['phone_number']).first() is None:
        lab_tech.phone_number = data['phone_number']

    db.session.commit()
    return jsonify({
        'id': lab_tech.id,
        'name': lab_tech.name,
        'email': lab_tech.email,
        'phone_number': lab_tech.phone_number
    }), 200


@app.route('/lab_techs/<int:id>', methods=['DELETE'])
def delete_lab_tech(id):
    lab_tech = LabTech.query.get(id)
    if not lab_tech:
        return jsonify({'message': 'Lab Tech not found'}), 404

    db.session.delete(lab_tech)
    db.session.commit()
    return jsonify({'message': 'Lab Tech deleted successfully'}), 200


# Routes for Test Report Management
@app.route('/test_reports', methods=['POST'])
def create_test_report():
    data = request.get_json()
    test_id = data.get('test_id')
    test = Test.query.get(test_id)
    if not test:
        return jsonify({'message': 'Test not found'}), 404

    test_report = TestReport(
        test_id=test.id,
        parameter=data.get('parameter', 'Default Parameter'),
        result=data.get('result', 'Default Result'),
        remark=data.get('remark', 'Normal'),
        created_at=datetime.utcnow()
    )
    db.session.add(test_report)
    db.session.commit()

    return jsonify({'message': 'Test report created successfully!'}), 201


@app.route('/test_reports', methods=['GET'])
def get_all_test_reports():
    test_reports = TestReport.query.all()
    return jsonify([
        {
            'id': report.id,
            'test_id': report.test_id,
            'parameter': report.parameter,
            'result': report.result,
            'remark': report.remark,
            'created_at': report.created_at
        }
        for report in test_reports
    ]), 200


@app.route('/test_reports/<int:id>', methods=['GET'])
def get_test_report(id):
    test_report = TestReport.query.get(id)
    if not test_report:
        return jsonify({'message': 'Test report not found'}), 404

    return jsonify({
        'id': test_report.id,
        'test_id': test_report.test_id,
        'parameter': test_report.parameter,
        'result': test_report.result,
        'remark': test_report.remark,
        'created_at': test_report.created_at
    }), 200


@app.route('/test_reports/<int:id>', methods=['PUT'])
def update_test_report(id):
    test_report = TestReport.query.get(id)
    if not test_report:
        return jsonify({'message': 'Test report not found'}), 404

    data = request.get_json()
    test_report.parameter = data.get('parameter', test_report.parameter)
    test_report.result = data.get('result', test_report.result)
    test_report.remark = data.get('remark', test_report.remark)

    db.session.commit()
    return jsonify({'message': 'Test report updated successfully!'}), 200


@app.route('/test_reports/<int:id>', methods=['DELETE'])
def delete_test_report(id):
    test_report = TestReport.query.get(id)
    if not test_report:
        return jsonify({'message': 'Test report not found'}), 404

    db.session.delete(test_report)
    db.session.commit()
    return jsonify({'message': 'Test report deleted successfully!'}), 200

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
    payment_method = "cash"  # Defaulting payment method to cash

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


if __name__ == '__main__':
    app.run(port=5555, debug=True)