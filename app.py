from flask import Flask, request, render_template, flash, redirect, url_for, session, logging
from data import jobs
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'jobershub'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init MySQL
mysql = MySQL(app)

jobs = jobs()


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/companyReviews')
def companyReviews():
    return render_template('companyReviews.html', jobss=jobs)

@app.route('/companyDetails/<string:id>/')
def companyDetails(id):
    return render_template('companyDetails.html', id=id)

# Check if the user is logged_in
def wrapper(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized user, Please login to continue', 'danger')
            return redirect(url_for('login'))
    return wrapped

class RegisterForm(Form):
    email = StringField('Email', [validators.length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        password =sha256_crypt.encrypt(str(form.password.data))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(email, password) VALUES(%s, %s)", (email, password))
        mysql.connection.commit()
        cur.close()

        flash('Registered Successfully!!', 'success')

        redirect(url_for('login'))

    return render_template('register.html', form=form)
  
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_candidate = request.form['password']

        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE email = %s", [email])

        if result > 0:
            data = cur.fetchone()
            password = data['password'] 

            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['email'] = email

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error)
            cursor.close()    
        else:
            error = 'User not found'
            return render_template('login.html', error=error)
            
    return render_template('login.html')

# Dashboard route
@app.route('/dashboard', methods=['GET', 'POST'])
@wrapper
def dashboard():
    return render_template('dashboard.html')


# Logout
@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    session.clear()
    flash('logged out successfully!', 'success')
    return redirect(url_for('login'))



#Profile
@app.route('/profile')
def profile():
    return render_template('profile.html')

if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)