from typing import List, Dict
import mysql.connector
# import simplejson as json
from flask import Flask, Response, flash, request, redirect, url_for, session, logging, render_template
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from functools import wraps

app = Flask(__name__)
config = {
    'user': 'root',
    'password': 'root',
    'host': 'db',
    'port': '3306',
    'database': 'covidData'
}

def covidData_import() -> List[Dict]:

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)

    cursor.execute('SELECT * FROM tblCount')
    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return result


@app.route('/graph')
def index():
    # user = {'username': 'Viha'}
    student_data = covidData_import()
    # print(student_data)
    labels = [row['Month'] for row in student_data]
    values = [row['count'] for row in student_data]
    return render_template('graph.html', labels=labels, values=values)


#
# @app.route('/api/students')
# def students() -> str:
#     js = json.dumps(studentData_import())
#     resp = Response(js, status=200, mimetype='application/json')
#     return resp
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=30)])
    username = StringField('Username', [validators.Length(min=4, max=20)])
    email = StringField('Email', [validators.Length(min=5, max=30)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():

        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)

        cursor.execute("INSERT INTO users (name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # commit
        connection.commit()

        # close connection
        cursor.close()
        connection.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)

        # Get user by username
        result = cursor.execute("SELECT * FROM users WHERE username = %s", [username])

        if result != 0:
            # Get stored hash
            data = cursor.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('index'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cursor.close()
            connection.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')


# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(host='0.0.0.0')
