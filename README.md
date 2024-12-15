Certificate Verification System

Overview

The Certificate Management System is a Flask-based web application designed to manage student certificates. It includes features for user registration, login, certificate creation, and verification. The application ensures the authenticity of certificates using secure hashing and digital signatures.

Features

User Authentication:

Secure registration and login using SHA-256 for password hashing.

Session-based authentication.

Certificate Creation:

Generate unique certificates with consistent IDs based on student data.

Securely sign certificates using RSA private keys.

Generate PDF certificates with QR codes for hash and signature values.

Certificate Verification:

Verify certificates using stored hash values and RSA digital signatures.

Provide verification feedback to users.

Prerequisites

To run this project, you need the following installed on your system:

Python 3.8 or higher

MySQL Server

Installation

Clone the Repository

$ git clone https://github.com/your-repo/certificate-management-system.git
$ cd certificate-management-system

Set Up Virtual Environment

$ python -m venv venv
$ source venv/bin/activate   # On Windows: venv\Scripts\activate

Install Dependencies

$ pip install -r requirements.txt

Configure MySQL Database

Create a MySQL database named certificate_db.

Import the database schema from schema.sql (if available):

$ mysql -u root -p certificate_db < schema.sql

Update app.config in the app.py file with your MySQL credentials:

app.config['MYSQL_USER'] = 'your_mysql_user'
app.config['MYSQL_PASSWORD'] = 'your_mysql_password'

Add RSA Keys

Generate RSA key pairs if not available:

$ openssl genrsa -out private_key.pem 2048
$ openssl rsa -in private_key.pem -pubout -out public_key.pem

Place the private_key.pem and public_key.pem files in the project root directory.

Run the Application

$ flask run

Visit the application at http://127.0.0.1:5000/.

Usage

1. Registration and Login

Navigate to the Register page to create an account.

Log in with your credentials to access certificate management features.

2. Create Certificate

Go to the Create Certificate page.

Fill in the student details (name, course, grade, issue date).

Generate the certificate as a downloadable PDF.

3. Verify Certificate

Go to the Verify Certificate page.

Provide the certificate ID, hash value, and digital signature to verify its authenticity.

Project Structure

certificate-management-system/
├── templates/                # HTML templates for the app
├── static/                   # Static files (CSS, JS, images)
├── app.py                    # Main application logic
├── schema.sql                # Database schema
├── private_key.pem           # RSA private key
├── public_key.pem            # RSA public key
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation

Technologies Used

Backend: Flask, Flask-MySQLdb

Frontend: HTML, CSS

Database: MySQL

PDF Generation: FPDF

Cryptography: PyCryptodome

QR Code Generation: qrcode library

Security Measures

Passwords hashed using SHA-256 before storing in the database.

Certificates signed with RSA private keys and verified using RSA public keys.

QR codes for easy sharing and validation of hash and signature values.

Future Improvements

Implement role-based access (e.g., admin vs. user).

Add certificate expiration and revocation features.

Enhance UI/UX with modern frontend frameworks.

Use environment variables for sensitive configurations.

License

This project is licensed under the MIT License. See the LICENSE file for more details.

Author

webhacer


