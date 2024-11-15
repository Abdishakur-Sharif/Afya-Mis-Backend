from models import db, Doctor,  Diagnosis,  LabTech, Patient, Payment, Consultation,ConsultationNotes ,Prescription, Medicine, Test, TestType, Appointment,DiagnosisNotes
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
from flask_migrate import Migrate
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





if __name__ == '__main__':
    app.run(port=5555, debug=True)
