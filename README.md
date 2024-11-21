Afya-Mis - Backend
The Afya-Mis backend is built to handle database interactions, process user requests, and manage MPESA payment integration for hospital operations.

Technologies Used
Flask: A lightweight Python web framework for creating RESTful APIs.

SQLAlchemy: An ORM for database management.

SQLite/PostgreSQL: Relational databases for persistent data storage.

MPESA API: Integrated for secure payment processing.

Datetime: A Python module for handling date and time operations.

Installation Guide
Clone the Repository
bash
Copy code
git clone https://github.com/Abdishakur-Sharif/Afya-Mis-Backend.git
cd Afya-Mis-Backend
Create and Activate a Virtual Environment
bash
Copy code
python3 -m venv venv
source venv/bin/activate       # For macOS/Linux
venv\Scripts\activate          # For Windows
Install Dependencies
bash
Copy code
pip install -r requirements.txt
Set Up the Database
bash
Copy code
flask db init
flask db migrate
flask db upgrade
Start the Flask Server
bash
Copy code
flask run
The backend API will be accessible at:
https://afya-mis-backend-6.onrender.com/

API Endpoints
Lab Technician Management
GET /lab_techs/<int:lab_tech_id>: Retrieve lab technician details.
POST /lab_techs: Create a new lab technician record.
PATCH /lab_techs/<int:id>: Update details of a lab technician.
DELETE /lab_techs/<int:id>: Delete a lab technician record.
Test Report Management
GET /test_reports: Fetch all test reports or filter by test ID.
POST /test_reports: Create a new test report.
Payment Management
GET /payments: Retrieve all payments.
GET /payments/<int:payment_id>: Fetch payment details by ID.
POST /payments: Process a new payment.
POST /payments/mpesa: Initiate an MPESA payment request.
MPESA Integration
To enable MPESA payment processing:

Configure MPESA API credentials as environment variables in a .env file:

bash
Copy code
MPESA_CONSUMER_KEY=your_mpesa_consumer_key
MPESA_CONSUMER_SECRET=your_mpesa_consumer_secret
MPESA_BASE_URL=https://sandbox.safaricom.co.ke
Use the /payments/mpesa endpoint to initiate payments.

Set up a callback URL to handle payment responses from MPESA.

Database Models
Lab Technician
id: Unique identifier (Primary Key).
name: Full name.
email: Email address.
phone_number: Contact number.

Test Report
id: Unique identifier (Primary Key).
test_id: Foreign key to the Test model.
result: Test result.
remarks: Additional notes.
created_at: Timestamp.
Payment

id: Unique identifier (Primary Key).
patient_id: Foreign key linking to the Patient model.
amount: Total paid amount.
payment_method: Method (e.g., Cash, MPESA).

Testing
Test endpoints and API integrations using pytest or unittest.
Example test cases:
Create and update lab technicians.
Generate test reports for patients.
Process payments via MPESA and validate callbacks.

Contributing
Fork the repository to your GitHub account.
Create a new branch for your changes.
Implement changes and write appropriate tests.
Submit a pull request with details of your changes.
