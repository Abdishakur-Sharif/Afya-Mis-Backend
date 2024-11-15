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
