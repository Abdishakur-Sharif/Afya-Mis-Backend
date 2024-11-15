from models import db, Doctor, Staff, Diagnosis,  LabTech, Patient, Payment, Consultation, Prescription, Medicine, Test, TestType, Appointment
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

if __name__ == '__main__':
    app.run(port=5555, debug=True)