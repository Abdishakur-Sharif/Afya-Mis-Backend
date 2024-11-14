from models import db, Doctor,  Diagnosis,  LabTech, Patient, Payment, Consultation,ConsultationNotes ,Prescription, Medicine, Test, TestType, Appointment
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

api.add_resource(Patients, '/patients', '/patients/<int:patient_id>')
api.add_resource(Consultations, '/consultations', '/consultations/<int:consultation_id>')  
api.add_resource(Notes, '/consultation_notes', '/consultation_notes/<int:consultationNotes_id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)