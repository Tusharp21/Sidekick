import datetime
import random
import time
from flask import Flask, render_template, request, url_for, session, redirect, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import json
import os
from flask_mail import Mail, Message
import smtplib
from smtplib import SMTPException
import requests

app = Flask(__name__)

app.secret_key = "your secret key"

#  MySQL Database Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "sidekick"

mysql = MySQL(app)


# app.config['MAIL_SERVER'] = 'aspmx.l.google.com'
# app.config['MAIL_PORT'] = 25

# Configuration for Flask-Mail (email sender)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587  # Use 587 for TLS and 465 for SSL
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = "sidekick.webtech@gmail.com"
app.config["MAIL_PASSWORD"] = "qkugbsmfwkugymme"
app.config["MAIL_DEFAULT_SENDER"] = "sidekick.webtech@gmail.com"

mail = Mail(app)

# A dictionary to store user data (you should use a database in production)
users = {}


# Generate a random 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))


# A decorator used to tell the application
# which URL is associated function


@app.route("/")
def home():
    return render_template("Home.html")


@app.route("/test")
def test():
    email = "anythingworksaslonasitwork@gmail.com"
    otp = generate_otp()

    try:
        # Send OTP via email
        msg = Message("OTP Verification", recipients=[email])
        msg.body = f"Your OTP is: {otp}"
        mail.send(msg)
        flash("OTP sent to your email. Please verify your email.")
        return "message sent"
    except SMTPException as e:
        # Handle email sending errors
        error_message = f"An error occurred while sending the email: {str(e)}"
        flash(error_message)
        return "message not sent" + error_message
    # return render_template('test.html')


@app.route("/course")
def course():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM course")
    courses = cursor.fetchall()
    return render_template("course.html", courses=courses)


@app.route("/admin")
def admin():
    return render_template("admin_panel.html")


@app.route("/project")
def project():
    if session.get("loggedin"):
        project_folder = "project_folder"  # Replace with the actual folder name
        file_list = os.listdir(project_folder)
        return render_template("project.html", files=file_list)
    else:
        return render_template("login.html")


# paymentgateway code start


@app.route("/payment_gateway", methods=["POST"])
def payment_gateway():
    if request.method == "POST" and "amount" in request.form:
        session["amount"] = request.form["amount"]
        amount = request.form["amount"]
        pa = "7587140713@paytm"
        pn = "Sidekick"
        cu = "INR"
        tn = "Sidekick Project"
        tr = ""
        am = amount

        phonepe_url = f"phonepe://pay?pa={pa}&pn={pn}&cu={cu}&tn={tn}&tr={tr}&am={am}"
        upi_url = f"upi://pay?pa={pa}&pn={pn}&cu={cu}&tn={tn}&tr={tr}&am={am}"

        return render_template(
            "payment_gateway.html",
            phonepe_url=phonepe_url,
            upi_url=upi_url,
            amount=amount,
        )


@app.route("/upload", methods=["POST"])
def upload_file():
    if "image" in request.files:
        file = request.files["image"]
        amount = session["amount"]
        user_id = session["id"]
        product_name = session["internship_type"]
        purchase_date = datetime.date.today()

        if file.filename != "":
            randi = str(random.randint(1, 1000))
            phone = str(session["phone"])
            custom_file_name = (
                session["username"] + phone + "-" + str(randi)
            )  # Replace with your desired custom file name
            app.config["bill_folder"] = "Bill_folder"
            target_directory = app.config["bill_folder"]
            target_path = os.path.join(target_directory, f"{custom_file_name}.png")
            file.save(target_path)

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "INSERT INTO purchases VALUES (NULL, % s, % s, % s, % s, % s, % s)",
                (
                    user_id,
                    product_name,
                    purchase_date,
                    target_path,
                    "admin review",
                    amount,
                ),
            )
            mysql.connection.commit()
            intern_final_msg = (
                "You have successfully Submitted ScreenShot Wait for Admin Approval !"
            )

            return render_template("dashboard.html", intern_final_msg=intern_final_msg)

    return "Error uploading file."


# payment gateway code end


@app.route("/starter")
def starter():
    return render_template("starter.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    msg = ""
    if (
        request.method == "POST"
        and "name" in request.form
        and "email" in request.form
        and "phone" in request.form
        and "project" in request.form
        and "message" in request.form
    ):
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        project = request.form["project"]
        message = request.form["message"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "INSERT INTO customer VALUES (NULL, %s, %s, %s, %s, %s, %s)",
            (
                name,
                phone,
                email,
                message,
                project,
                "Yet to Contact",
            ),
        )
        mysql.connection.commit()
        msg = "We Got Your Message in successfully! We will Contact you as soon as possible."
        
        return render_template("contact.html", msg=msg)
    else:
        return render_template("contact.html")


@app.route("/internship")
def internship():
    return render_template("internship.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    # this if is forregestering internship type
    if request.method == "POST" and "internship_type" in request.form:
        if not session.get("loggedin"):
            return render_template("login.html")
        else:
            session["internship_type"] = request.form["internship_type"]
            try:
                # Get the session variables 'internship_type' and 'username'
                internship_type = session.get("internship_type")
                username = session.get("username")

                # Get the session variables for intsernship table
                user_id = session["id"]
                join_date = datetime.date.today()

                if internship_type is not None and username is not None:
                    # Create a cursor
                    cur = mysql.connection.cursor()

                    # Update the 'accounts' table where 'username' matches the session's 'username'
                    cur.execute(
                        "UPDATE accounts SET internship = %s WHERE username = %s",
                        (internship_type, username),
                    )

                    # inserting the data in internship table
                    cur.execute

                    # Update the 'accounts' table where 'username' matches the session's 'username'
                    cur.execute(
                        "INSERT INTO internship VALUES (NULL, %s, %s, %s, %s, %s, %s)",
                        (
                            user_id,
                            internship_type,
                            join_date,
                            "Not set",
                            "Not set",
                            "0",
                        ),
                    )

                    # inserting the data in internship table
                    cur.execute

                    # Commit the changes and close the cursor
                    mysql.connection.commit()
                    cur.close()

                    project_folder = (
                        "project_folder"  # Replace with the actual folder name
                    )
                    file_list = os.listdir(project_folder)
                    return render_template("dashboard.html", files=file_list)
            except Exception as e:
                return str(e)

    # this if is for registering git link of intern
    if request.method == "POST" and "git_link" in request.form:
        try:
            # Get the session variables 'username' and 'git_link' from form
            git_link = request.form["git_link"]
            username = session.get("username")

            if git_link is not None and username is not None:
                # Create a cursor
                cur = mysql.connection.cursor()

                # Update the 'accounts' table where 'username' matches the session's 'username'
                cur.execute(
                    "UPDATE accounts SET task_status = %s WHERE username = %s",
                    (git_link, username),
                )

                # Commit the changes and close the cursor
                mysql.connection.commit()
                cur.close()

                session["git_link"] = git_link

                intern_msg = "Link Uploaded Successfully"

                project_folder = (
                    "project_folder"  # Project folder containing projects with name
                )
                file_list = os.listdir(project_folder)
                return render_template(
                    "dashboard.html", files=file_list, intern_msg=intern_msg
                )
        except Exception as e:
            return str(e)

    if not session.get("loggedin"):
        return render_template("login.html")
    else:
        project_folder = (
            "project_folder"  # Project folder containing projects with name
        )
        file_list = os.listdir(project_folder)
        return render_template("dashboard.html", files=file_list)


@app.route('/send_otp', methods=['POST'])
def send_otp():
    if request.method == "POST" and "phone_number" in request.form:
        phone_number = request.form.get('phone_number')
        session['phone'] = request.form.get('phone_number')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT phone FROM accounts WHERE phone = % s",(phone_number, ),)
        phone = cursor.fetchone()
        
        if phone:
            # Generate a random 6-digit OTP
            import random
            otp = str(random.randint(100000, 999999))

            # Store the OTP in the user's session
            session['otp'] = otp

            # Send OTP via Fast2SMS API
            url = f'https://www.fast2sms.com/dev/bulkV2'
            params = {
                'authorization': 'AJdoFf7yuQOjWXBVRpszi4xKvcDa3Gn1Nm2krUIg98CEtehP0lFOmbB8ShnDLi1MgYRp0XtIQHe2r7jP',
                'route': 'otp',
                'variables_values': otp,
                'flash': '0',
                'numbers': phone_number,
                # 'template_id': OTP_TEMPLATE_ID,
            }

            response = requests.get(url, params=params)
            data = response.json()
            
            if data['return'] == True:
                flash('OTP sent successfully!', 'success')
                return redirect(url_for('verify_otp'))
            else:
                flash('Failed to send OTP. Please try again.', 'error')
                return redirect(url_for('home'))
        else:
            return redirect(url_for('register'))
        
    elif request.method == "POST" and "email" in request.form:
        email = request.form["email"]
        session["email"] = request.form["email"]

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT email FROM accounts WHERE email = % s",(email, ),)
        email = cursor.fetchone()
        if email:
            otp = generate_otp()
            session["otp"] = otp
            try:
                # Send OTP via email
                msg = Message("OTP Verification", recipients=[email["email"]])
                msg.body = f"Your OTP is: " + str(otp)
                mail.send(msg)
                flash("OTP sent to your email. Please verify your email.")
                return redirect(url_for('verify_otp', email=email))
            except SMTPException as e:
                # Handle email sending errors
                error_message = f"An error occurred while sending the email: {str(e)}"
                flash(error_message)
                msg = "message not sent" + error_message
                return render_template("login.html",msg=msg)
    else:
        return render_template("login.html")    


@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if session.get('phone'):
        phone_number = session.get('phone')
        if request.method == 'POST':
            entered_otp = request.form.get('otp')
            stored_otp = session.get('otp')
            if stored_otp and entered_otp == stored_otp:
                flash('OTP verification successful!', 'success')
                session.pop('otp')
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM accounts WHERE phone = % s",
                (
                    phone_number,
    
                ),)
            account = cursor.fetchone()
            if account:
                session["loggedin"] = True
                session["id"] = account["id"]
                session["username"] = account["username"]
                session["phone"] = account["phone"]
                session["email"] = account["email"]
                session["internship_type"] = account[
                    "internship"
                ]  # defines interns and their type in dashboard
                session["git_link"] = account["task_status"]
                # msg = 'Logged in successfully !'
                return redirect(url_for("home"))
                # return redirect(url_for('dashboard'))
            else:
                flash('Incorrect OTP. Please try again.', 'error')
    elif session.get('email'):
        if request.method == 'POST':
            entered_otp = request.form.get('otp')
            stored_otp = session.get('otp')
            email = session.get('email')
            if stored_otp and entered_otp == stored_otp:
                flash('OTP verification successful!', 'success')
                session.pop('otp')
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("SELECT * FROM accounts WHERE email = % s",(email, ),)
                account = cursor.fetchone()
                if account:
                    session["loggedin"] = True
                    session["id"] = account["id"]
                    session["username"] = account["username"]
                    session["phone"] = account["phone"]
                    session["email"] = account["email"]
                    session["internship_type"] = account[
                        "internship"
                    ]  # defines interns and their type in dashboard
                    session["git_link"] = account["task_status"]
                    # msg = 'Logged in successfully !'
                    return redirect(url_for("home"))
                    # return redirect(url_for('dashboard'))
                else:
                    return render_template("register.html")
            else:
                flash('Incorrect OTP. Please try again.', 'error')

    return render_template('verify_otp.html')


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    msg=''
    if request.method == 'POST' and 'phone_number' in request.form:
        phone_number = request.form['phone_number']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM accounts WHERE phone = % s",(phone_number, ),)
        account = cursor.fetchone()
        if account:
            password = 'your password is ' + str(account["phone"])
            # Send OTP via Fast2SMS API
            url = f'https://www.fast2sms.com/dev/bulkV2'
            params = {
                'authorization': 'AJdoFf7yuQOjWXBVRpszi4xKvcDa3Gn1Nm2krUIg98CEtehP0lFOmbB8ShnDLi1MgYRp0XtIQHe2r7jP',
                'route': 'otp',
                'variables_values': password,
                'flash': '0',
                'numbers': phone_number,
                # 'template_id': OTP_TEMPLATE_ID,
            }

            response = requests.get(url, params=params)
            data = response.json()
            
            if data['return'] == True:
                flash('OTP sent successfully!', 'success')
                return redirect(url_for('login'))
        else:
            msg = 'Number is Not Registered'
            return render_template('forgot_password.html', msg=msg)
    elif request.method == 'POST' and 'email' in request.form:
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM accounts WHERE email = % s",(email, ),)
        account = cursor.fetchone()
        if account:
            password = account["password"]
            try:
                # Send OTP via email
                msg = Message("OTP Verification", recipients=[email])
                msg.body = f"Your Password is: {password}"
                mail.send(msg)
                flash("OTP sent to your email. Please verify your email.")
                return redirect(url_for('login'))
            except SMTPException as e:
                # Handle email sending errors
                error_message = f"An error occurred while sending the email: {str(e)}"
                flash(error_message)
                msg = "message not sent" + error_message
                return render_template('forgot_password.html',msg=msg)

        else:
            msg = 'Email is Not Registered'
            return render_template('forgot_password.html', msg=msg)
    else:
        return render_template('forgot_password.html',msg=msg)


@app.route("/login", methods=["GET", "POST"])
def login():
    otp = generate_otp()
    msg = ""
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM accounts WHERE username = % s AND password = % s",
            (
                username,
                password,
            ),
        )
        account = cursor.fetchone()
        if account:
            session["loggedin"] = True
            session["id"] = account["id"]
            session["username"] = account["username"]
            session["phone"] = account["phone"]
            session["email"] = account["email"]
            session["internship_type"] = account[
                "internship"
            ]  # defines interns and their type in dashboard
            session["git_link"] = account["task_status"]
            # msg = 'Logged in successfully !'
            return redirect(url_for("home"))
        else:
            msg = "Incorrect username / password !"
            return render_template("login.html", msg=msg)
    else:
        return render_template("login.html", msg=msg, otp=otp)


@app.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    session.pop("phone", None)
    session.pop("email", None)
    session.pop("internship_type", None)
    session.pop("git_link", None)
    # return redirect(url_for('login'))
    return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ""
    otp = generate_otp()
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
        and "email" in request.form
        and "fname" in request.form
        and "lname" in request.form
        and "phone" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        first_name = request.form["fname"]
        last_name = request.form["lname"]
        phone = request.form["phone"]
        print(phone)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM accounts WHERE username = % s", (username,))
        account = cursor.fetchone()
        if account:
            msg = "Account already exists ! \n Try a different Username"
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            msg = "Invalid email address !"
        elif not re.match(r"[A-Za-z0-9]+", username):
            msg = "Username must contain only characters and numbers !"
        elif not username or not password or not email:
            msg = "Please fill out the form !"
        else:
            cursor.execute(
                "INSERT INTO accounts VALUES (NULL, % s, % s, % s, % s, % s, % s, NULL, NULL)",
                (
                    username,
                    password,
                    email,
                    first_name,
                    last_name,
                    phone,
                ),
            )
            mysql.connection.commit()
            msg = "You have successfully registered !"
    elif request.method == "POST":
        msg = "Please fill out the form !"
    return render_template("register.html", msg=msg, otp=otp)


if __name__ == "__main__":
    app.run(debug=True)
