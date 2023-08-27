from flask import Flask, render_template, request, url_for
from flask_mysqldb import MySQL
import json
import os

app = Flask(__name__)


# A decorator used to tell the application
# which URL is associated function
@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # getting input with name = fname in HTML form
        phone_number = request.form.get("phone")
        return phone_number
    return render_template('Home.html')


@app.route("/project")
def project():
    return render_template('project.html')


app.run(debug=True)
