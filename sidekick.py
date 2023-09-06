import datetime
import random
import time
from flask import Flask, render_template, request, url_for, session, redirect, flash
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

@app.route('/admin')
def admin():
    return render_template('admin_panel.html')


@app.route("/project")
def project():
    if session.get('loggedin'):
        project_folder = 'project_folder'  # Replace with the actual folder name
        file_list = os.listdir(project_folder)
        return render_template('project.html', files=file_list)
    else:
        return render_template('login.html')

# paymentgateway code start

@app.route("/payment_gateway", methods=['POST'])
def payment_gateway():
    if request.method == 'POST' and 'amount' in request.form:
        session['amount'] = request.form['amount']
        amount = request.form['amount']
        pa = "7587140713@paytm"
        pn = "Sidekick"
        cu = "INR"
        tn = "Sidekick Project"
        tr = ""
        am = amount

        phonepe_url = f"phonepe://pay?pa={pa}&pn={pn}&cu={cu}&tn={tn}&tr={tr}&am={am}"
        upi_url = f"upi://pay?pa={pa}&pn={pn}&cu={cu}&tn={tn}&tr={tr}&am={am}"

        return render_template('payment_gateway.html', phonepe_url=phonepe_url, upi_url=upi_url, amount = amount)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' in request.files:
        file = request.files['image']
        amount = session['amount']
        user_id = session['id']
        product_name = session['internship_type']
        purchase_date = datetime.date.today()

        if file.filename != '':
            randi = str(random.randint(1, 1000))
            custom_file_name = session['username'] + session['phone'] + '-' + randi # Replace with your desired custom file name
            app.config['bill_folder'] = 'Bill_folder'
            target_directory = app.config['bill_folder']
            target_path = os.path.join(target_directory, f"{custom_file_name}.png")
            file.save(target_path)

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO purchases VALUES (NULL, % s, % s, % s, % s, % s, % s)', (user_id, product_name, purchase_date, target_path, 'admin review', amount,))
            mysql.connection.commit()
            intern_final_msg = 'You have successfully Submitted ScreenShot Wait for Admin Approval !'

            return render_template('dashboard.html', intern_final_msg = intern_final_msg)

    
    return "Error uploading file."

# payment gateway code end


@app.route("/starter")
def starter():
    return render_template('starter.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/internship")
def internship():
    return render_template('internship.html')

@app.route("/dashboard", methods =['GET', 'POST'])
def dashboard():
    # this if is forregestering internship type
    if request.method == 'POST' and 'internship_type' in request.form:
        if not session.get('loggedin'):
            return render_template('login.html')
        else:
            session['internship_type'] = request.form['internship_type']
            try:
                # Get the session variables 'internship_type' and 'username'
                internship_type = session.get('internship_type')
                username = session.get('username')

                # Get the session variables for intsernship table
                user_id = session['id']
                join_date = datetime.date.today()

                if internship_type is not None and username is not None:
                    # Create a cursor
                    cur = mysql.connection.cursor()
                    
                    # Update the 'accounts' table where 'username' matches the session's 'username'
                    cur.execute("UPDATE accounts SET internship = %s WHERE username = %s", (internship_type, username))
                    
                    # inserting the data in internship table
                    cur.execute
                    
                    # Update the 'accounts' table where 'username' matches the session's 'username'
                    cur.execute("INSERT INTO internship VALUES (NULL, %s, %s, %s, %s, %s, %s)", (user_id, internship_type, join_date, 'Not set', 'Not set', '0'))
                    
                    # inserting the data in internship table
                    cur.execute
                    
                    # Commit the changes and close the cursor
                    mysql.connection.commit()
                    cur.close()
                    
                    project_folder = 'project_folder'  # Replace with the actual folder name
                    file_list = os.listdir(project_folder)
                    return render_template('dashboard.html', files = file_list)
            except Exception as e:
                return str(e)
    
    # this if is for registering git link of intern 
    if request.method == 'POST' and 'git_link' in request.form:
        try:
            # Get the session variables 'username' and 'git_link' from form
            git_link = request.form['git_link']
            username = session.get('username')
            
            if git_link is not None and username is not None:
                # Create a cursor
                cur = mysql.connection.cursor()
                
                # Update the 'accounts' table where 'username' matches the session's 'username'
                cur.execute("UPDATE accounts SET task_status = %s WHERE username = %s", (git_link, username))
                
                # Commit the changes and close the cursor
                mysql.connection.commit()
                cur.close()

                session['git_link'] = git_link

                intern_msg = 'Link Uploaded Successfully'  
                
                project_folder = 'project_folder'  # Project folder containing projects with name
                file_list = os.listdir(project_folder)
                return render_template('dashboard.html', files = file_list, intern_msg = intern_msg)
        except Exception as e:
            return str(e)
        
    if not session.get('loggedin'):
        return render_template('login.html')
    else:
        project_folder = 'project_folder'  # Project folder containing projects with name
        file_list = os.listdir(project_folder)
        return render_template('dashboard.html', files = file_list)

        
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
            session['phone'] = account['phone'] 
            session['email'] = account['email'] 
            session['internship_type'] = account['internship']  #defines interns and their type in dashboard
            session['git_link'] = account['task_status']
            session['image'] = account['image']
            # msg = 'Logged in successfully !' 
            return render_template('home.html')
        else:
            msg = 'Incorrect username / password !'
            return render_template('login.html', msg = msg)
    else: 
       return render_template('login.html', msg = msg)
        
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('internship_type', None)
    session.pop('git_link', None)
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