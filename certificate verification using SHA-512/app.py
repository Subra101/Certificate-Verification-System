from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file				
from flask_mysqldb import MySQL
from hashlib import sha512
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA512
from fpdf import FPDF
import io
import os
import qrcode
from io import BytesIO
import random
import string
import hashlib

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '2005'
app.config['MYSQL_DB'] = 'certificate_db'
app.secret_key = 'your_secret_key'

mysql = MySQL(app)


def generate_pdf(student_data, username, hash_value, signed_data, certificate_id):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
  
    pdf.cell(200, 10, txt="Student Certificate", ln=True, align='C')
    
    
    pdf.ln(10)  
    pdf.cell(200, 10, txt=f"Certificate ID: {certificate_id}", ln=True, align='C')
    
   
    pdf.ln(10)
    pdf.multi_cell(0, 10, f"Student Data:\n{student_data}")
    
   
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Generated by: {username}", ln=True)

    
    os.makedirs("qrcodes", exist_ok=True)
    hash_qr_path = os.path.join("qrcodes", "hash_qr.png")
    signature_qr_path = os.path.join("qrcodes", "signature_qr.png")

   
    hash_qr = qrcode.make(hash_value)
    hash_qr.save(hash_qr_path)
    signature_qr = qrcode.make(signed_data)
    signature_qr.save(signature_qr_path)

    
    pdf.ln(5)
    pdf.cell(200, 10, txt="Hash Value (QR Code):", ln=True)
    pdf.image(hash_qr_path, x=10, y=pdf.get_y() + 5, w=50, h=50)

    pdf.set_y(pdf.get_y() + 60)
    pdf.cell(200, 10, txt="Signature (QR Code):", ln=True)
    pdf.image(signature_qr_path, x=10, y=pdf.get_y() + 5, w=50, h=50)

   
    pdf_output = BytesIO()
    pdf_output.write(pdf.output(dest='S').encode('latin1'))
    pdf_output.seek(0)

   
    try:
        os.remove(hash_qr_path)
        os.remove(signature_qr_path)
    except FileNotFoundError:
        print("QR code files not found for cleanup.")

    return pdf_output


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        # Fetch the user from the database
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

       
        if user and user[2] == hashlib.sha256(password.encode()).hexdigest():  # user[2] is the password column
            session['username'] = username
            flash("Login successful!")
            return redirect(url_for('create_certificate'))
        else:
            flash("Invalid credentials. Please try again.")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        cur = mysql.connection.cursor()

        
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        
        if user:
            flash("Username already taken, please choose another.")
            cur.close()
            return redirect(url_for('register'))

      
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        cur.close()
        
        flash("Registration successful! You can now log in.")
        return redirect(url_for('login'))

    return render_template('register.html')

    
def generate_certificate_id_from_data(student_data):
    """Generate a consistent certificate ID based on student data."""
    # Create a salt and use it with the student data to ensure unique, consistent ID
    salt = random.choice(string.ascii_letters + string.digits)
    unique_data = student_data + salt
    certificate_id = hashlib.sha256(unique_data.encode()).hexdigest()[:16]  # 16-char hash
    return certificate_id



@app.route('/create_certificate', methods=['GET', 'POST'])
def create_certificate():
    if 'username' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        student_name = request.form['student_name']
        course = request.form['course']
        grade = request.form['grade']
        issue_date = request.form['issue_date']
        
        student_data = f"Name: {student_name}\nCourse: {course}\nGrade: {grade}\nIssue Date: {issue_date}"
        hash_value = sha512(student_data.encode()).hexdigest()

        
        certificate_id = generate_certificate_id_from_data(student_data)

        
        private_key = RSA.import_key(open('private_key.pem').read())
        signer = pkcs1_15.new(private_key)
        signed_data = signer.sign(SHA512.new(student_data.encode())).hex()
        
        
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO certificates (certificate_id, student_data, hash_value, signed_data) VALUES (%s, %s, %s, %s)",
            (certificate_id, student_data, hash_value, signed_data)
        )
        mysql.connection.commit()
        
        cur.close()
        
        
        pdf_output = generate_pdf(student_data, session['username'], hash_value, signed_data, certificate_id)
        
       
        flash(f"Certificate created successfully! Certificate ID is: {certificate_id}")
        return send_file(pdf_output, as_attachment=True, download_name='certificate.pdf', mimetype='application/pdf')
    
    return render_template('create_certificate.html')



@app.route('/verify_certificate', methods=['GET', 'POST'])
def verify_certificate():
    verification_status = None
    
    if request.method == 'POST':
        
        certificate_id = request.form['certificate_id']
        hash_value = request.form['hash_value']
        signature = request.form['signature']
        
      
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT certificate_id, hash_value, signed_data FROM certificates WHERE certificate_id = %s", 
            (certificate_id,)
        )
        row = cur.fetchone()
        cur.close()

        
        if row:
            db_certificate_id, db_hash_value, db_signed_data = row

            
            match_count = 0

           
            if db_certificate_id == certificate_id:
                match_count += 1

           
            if db_hash_value == hash_value:
                match_count += 1

            
            try:
                public_key = RSA.import_key(open('public_key.pem').read())
                verifier = pkcs1_15.new(public_key)
                
                verifier.verify(SHA512.new(db_hash_value.encode()), bytes.fromhex(signature))
                match_count += 1  # Signature matched
            except (ValueError, TypeError):
                pass  

            
            if match_count >= 2:
                verification_status = "Certificate Verified Successfully!"
            else:
                verification_status = "Verification failed. Not enough matching values."
        else:
            verification_status = "Certificate not found."
    
    return render_template('verify_certificate.html', verification_status=verification_status)



if __name__ == '__main__':
    app.run(debug=True)
