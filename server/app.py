from models import db, Doctor,  Diagnosis,  LabTech, Patient, Payment, Consultation, Prescription, Medicine, Test, TestType, Appointment
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os
from flask import Flask, request, jsonify
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