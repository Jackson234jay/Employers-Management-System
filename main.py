from flask import Flask, render_template, request, redirect, url_for, flash, session
import pyrebase
from firebase_config import firebaseConfig, auth
from firebase_admin import credentials, db
import json
from datetime import datetime




app = Flask(__name__)
config = firebaseConfig()
app.secret_key = 'AIzaSyD0Mz01-HXTP1TyC_17XD5BMNEABBucino'
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

from flask_mail import Mail, Message

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'blossomjohn399@gmail.com'
app.config['MAIL_PASSWORD'] = 'xdmz ahsn yhhy pylh'

app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['Email']
        password = request.form['password']
        try:
            # Create a new user
            user = auth.create_user_with_email_and_password(email, password)
            flash('User created successfully!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            error_json = json.loads(e.args[1])  # Parse the error JSON string into a dictionary
            error_code = error_json.get('error', {}).get('message')  # Extract the error code from the JSON
            if error_code == "EMAIL_EXISTS":
                flash('Email Already Exists', 'danger')
            elif "WEAK_PASSWORD" in str(e):
                flash('Password is too weak. Please use a stronger password.', 'danger')
            elif "INVALID_EMAIL" in str(e):
                flash('Invalid email format. Please enter a valid email address.', 'danger')
            else:
                flash('Failed to create user.', 'danger')
            return redirect(url_for('register'))
    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['Email']
        password = request.form['password']
        try:
            # Attempt to sign in the user
            user = auth.sign_in_with_email_and_password(email, password)
            flash('Successfully logged in!', 'success')
            return redirect(url_for('add_organization'))
        except Exception as e:
            if len(e.args) > 1 and isinstance(e.args[1], str):
                error_json = json.loads(e.args[1])  # Parse the error JSON string into a dictionary
                error_code = error_json.get('error', {}).get('message')  # Extract the error code from the JSON
                if error_code == "EMAIL_NOT_FOUND":
                    flash('Email not found. Please register first.', 'danger')
                elif error_code == "INVALID_PASSWORD":
                    flash('Invalid password. Please try again.', 'danger')
                else:
                    flash('Failed to log in. Please try again.', 'danger')
            else:
                flash('Failed to log in. Please try again.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')



@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['Email']
        try:
            auth.send_password_reset_email(email)
            flash('Password reset email sent. Please check your inbox.', 'success')
        except Exception as e:
            error_json = e.args[1]
            error = json.loads(error_json)['error']
            if error['code'] == 'auth/user-not-found':
                flash('Email not found. Please register first.', 'danger')
            else:
                flash('Failed to send password reset email. Please try again.', 'danger')
        return redirect(url_for('reset_password'))
    return render_template('reset.html')

@app.route('/dashboard/<feature>')
def dashboard(feature):
    return render_template('Dashboard.html', feature=feature)

@app.route('/add_organization', methods=['GET', 'POST'])
def add_organization():
    if request.method == 'POST':
        org_data = {
            'name': request.form['org_name'],
            'address': request.form['org_address'],
            'phone': request.form['org_phone'],
            'email': request.form['org_email'],
            'description': request.form['org_description']
        }
        
        db = firebase.database()
        db.child("organizations").push(org_data)
        
        flash('Organization added successfully!', 'success')
        return redirect(url_for('dashboard', feature='overview'))
    
    return render_template('Organisation.html')

@app.route('/choose_organization')
def choose_organization():
    db = firebase.database()
    organizations = db.child("organizations").get().val()
    return render_template('choose_organization.html', organizations=organizations)

@app.route('/select_organization', methods=['POST'])
def select_organization():
    org_id = request.form['organization_id']
    # Store the selected organization ID in the session or user's data
    session['selected_organization'] = org_id
    return redirect(url_for('dashboard', feature='overview'))


# Get a reference to the database
ref = db.reference('staff')

@app.route('/staff', methods=['GET', 'POST'])
def staff_management():
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        new_staff = ref.push({
            'name': name,
            'position': position
        })
        return redirect(url_for('staff_management'))
    
    staff_data = ref.get()
    staff_list = [{'id': key, **value} for key, value in staff_data.items()] if staff_data else []
    return render_template('Dashboard.html', feature='staff', staff=staff_list)

@app.route('/edit_staff/<string:id>', methods=['GET', 'POST'])
def edit_staff(id):
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        ref.child(id).update({
            'name': name,
            'position': position
        })
        return redirect(url_for('staff_management'))
    
    staff_member = ref.child(id).get()
    return render_template('edit_staff.html', staff=staff_member, id=id)


@app.route('/delete_staff/<string:id>')
def delete_staff(id):
    ref.child(id).delete()
    return redirect(url_for('staff_management'))

@app.route('/payroll')
def payroll_management():
    staff_data = ref.get()
    payroll = []
    
    for key, employee in staff_data.items():
        monthly_salary = float(employee.get('monthly_salary', 0))
        overtime_hours = float(employee.get('overtime_hours', 0))
        overtime_rate = 1.5 * (monthly_salary / (4 * 40))  # Assuming 40-hour work week
        overtime_pay = overtime_hours * overtime_rate
        total_monthly_pay = monthly_salary + overtime_pay
        
        payroll.append({
            'name': employee['name'],
            'position': employee['position'],
            'monthly_salary': round(monthly_salary, 2),
            'overtime_pay': round(overtime_pay, 2),
            'total_monthly_pay': round(total_monthly_pay, 2)
        })
    
    return render_template('Dashboard.html', feature='payroll', payroll=payroll)

@app.route('/about us')
def about_us():
    return render_template('aboutus.html')

@app.route('/contactus', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        
        # Send email
        msg = Message(subject,
                      sender=email,
                      recipients=['blossomjohn399@gmail.com'])
        msg.body = f"From: {name}\nEmail: {email}\n\n{message}"
        mail.send(msg)
        
        # Store the message in Firebase (keep your existing code here)
        
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact_us'))
    
    return render_template('contactus.html')



if __name__ == '__main__':
    app.run(debug=True)
if __name__ == '__main__':
    app.run(debug=True)