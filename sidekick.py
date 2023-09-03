from flask import Flask, render_template, request, url_for, session, redirect
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import json
import os

app = Flask(__name__)

app.secret_key = 'your secret key'
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sidekick'
 
mysql = MySQL(app)
 
# A decorator used to tell the application
# which URL is associated function
@app.route('/')
def home():
    return render_template('Home.html')


@app.route("/project")
def project():
    project_folder = 'project_folder'  # Replace with the actual folder name
    file_list = os.listdir(project_folder)
    return render_template('project.html', files=file_list)


@app.route("/payment_gateway")
def payment_gateway():
    pa = "7587140713@paytm"
    pn = "Sidekick"
    cu = "INR"
    tn = "Sidekick Project"
    tr = ""
    am = "2500"

    phonepe_url = f"phonepe://pay?pa={pa}&pn={pn}&cu={cu}&tn={tn}&tr={tr}&am={am}"
    upi_url = f"upi://pay?pa={pa}&pn={pn}&cu={cu}&tn={tn}&tr={tr}&am={am}"

    return render_template('payment_gateway.html', phonepe_url=phonepe_url, upi_url=upi_url)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' in request.files:
        file = request.files['image']

        if file.filename != '':
            custom_file_name = "example_filename"  # Replace with your desired custom file name
            target_directory = app.config['UPLOAD_FOLDER']
            target_path = os.path.join(target_directory, f"{custom_file_name}.png")

            file.save(target_path)

            return "File uploaded successfully."
    
    return "Error uploading file."

@app.route("/starter")
def starter():
    return render_template('starter.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')


@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username'] 
            msg = 'Logged in successfully !'
            return render_template('home.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)
 
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # return redirect(url_for('login'))
    return redirect(url_for('home'))
 
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'fname' in request.form and 'lname' in request.form and 'phone' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        first_name = request.form['fname']
        last_name = request.form['lname']
        phone = request.form['phone']
        print(phone)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s, % s, % s, % s)', (username, password, email, first_name, last_name, phone,))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)


app.run(debug=True)