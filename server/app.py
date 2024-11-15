from models import db, Doctor,  Diagnosis,  LabTech, Patient, Payment, Consultation, Prescription, Medicine, Test, TestType, Appointment,DiagnosisNotes
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os
from flask import Flask, request, jsonify, abort
from datetime import datetime



BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

class Index(Resource):

    def get(self):
        response_dict = {
            "message": "Afya Mis"
        }
        response = make_response(
            response_dict,
            200
        )
        return response
    
api.add_resource(Index, '/')

# Add a route for patients
class Patients(Resource):
    def get(self, patient_id=None):
        if patient_id:
            # Fetch a single patient by ID
            patient = Patient.query.get(patient_id)
            
            # If no patient is found, return a 404 error
            if not patient:
                return make_response({"message": f"Patient with ID {patient_id} not found"}, 404)
            
            # Return only the specified fields
            patient_data = {
                "id": patient.id,
                "name": patient.name,
                "gender": patient.gender,
                "address": patient.address,
                "phone_number": patient.phone_number,
                "medical_history": patient.medical_history,
                "date_of_birth": patient.date_of_birth.isoformat()  # Ensure proper date format
            }
            
            return make_response(patient_data, 200)
        
        # Fetch all patients if no `patient_id` is provided
        patients = Patient.query.all()
        
        if not patients:
            return make_response({"message": "No patients found"}, 404)
        
        # Serialize the patient data into a list of dictionaries
        patient_data = [{
            "id": patient.id,
            "name": patient.name,
            "gender": patient.gender,
            "address": patient.address,
            "phone_number": patient.phone_number,
            "medical_history": patient.medical_history,
            "date_of_birth": patient.date_of_birth.isoformat()  # Ensure proper date format
        } for patient in patients]
        
        # Return the list of patients as a JSON response
        return make_response(patient_data, 200)


@app.route('/tests/<int:id>', methods=['DELETE'])
def delete_test(id):
    test = Test.query.get(id)
    if test is None:
        abort(404, description="Test not found")

api.add_resource(Patients, '/patients', '/patients/<int:patient_id>')  # Route with optional patient_id





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




if __name__ == '__main__':
    app.run(port=5555, debug=True)