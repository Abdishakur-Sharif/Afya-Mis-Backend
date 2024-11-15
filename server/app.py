from models import db, Doctor,  Diagnosis,  LabTech, Patient, Payment, Consultation,ConsultationNotes ,Prescription, Medicine, Test, TestType, Appointment
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
from flask_migrate import Migrate
import os
from datetime import datetime
from models import db, Patient , Medicine

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

if __name__ == '__main__':
    app.run(port=5555, debug=True)
