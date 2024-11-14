from models import db, Doctor,  Diagnosis,  LabTech, Patient, Payment, Consultation, Prescription, Medicine, Test, TestType, Appointment
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

class Appointments(Resource):

    def get(self):
        # Fetch all appointments from the database
        appointments = Appointment.query.all()

        response_dict_list = [
            {
                "id": appointment.id,  
                "appointment_date": appointment.appointment_date,
                "appointment_time": appointment.appointment_time,
                "patient": {
                    "id": appointment.patient.id,  
                    "name": appointment.patient.name,
                    "phone_number": appointment.patient.phone_number,
                    "gender": appointment.patient.gender,
                    "email": appointment.patient.email,
                },
                "doctor": {
                    "id": appointment.doctor.id,  
                    "name": appointment.doctor.name,
                    "phone_number": appointment.doctor.phone_number,
                    "email": appointment.doctor.email,
                },
            }
            for appointment in appointments
        ]
        response = make_response(response_dict_list, 200)
        return response
    
api.add_resource(Appointments, '/appointments')

class AppointmentByID(Resource):

    def get(self, id):
        appointment = Appointment.query.filter_by(id=id).first()

        # Check if appointment exists
        if appointment is None:
            response_dict = {
                "error": "Appointment not found"
            }
            response = make_response(response_dict, 404)
            return response

        appointment_dict = {
            "id": appointment.id,
            "appointment_date": appointment.appointment_date,
            "appointment_time": appointment.appointment_time,
            "patient": {
                "id": appointment.patient.id,
                "name": appointment.patient.name,
                "phone_number": appointment.patient.phone_number,
                "gender": appointment.patient.gender,
                "email": appointment.patient.email,
            },
            "doctor": {
                "id": appointment.doctor.id,
                "name": appointment.doctor.name,
                "phone_number": appointment.doctor.phone_number,
                "email": appointment.doctor.email,
            },
        }

        response = make_response(appointment_dict, 200)
        return response

api.add_resource(AppointmentByID, '/appointments/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)