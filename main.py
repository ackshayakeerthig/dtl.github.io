from flask import Flask, render_template, redirect, url_for, request, session, flash
import random
import string
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, URL, Length, ValidationError, Email, EqualTo,InputRequired
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

# Flask App Setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///donor_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
db = SQLAlchemy(app)

# Models
class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    num = db.Column(db.String(11), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    area = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    clothes = db.Column(db.String(50), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Forms
class DonorForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    num = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=10, message="Invalid phone number")])
    state = SelectField('State', validators=[DataRequired()], choices=[
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
        "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
        "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttarakhand", "Uttar Pradesh",
        "West Bengal", "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Lakshadweep",
        "Delhi", "Puducherry"
    ])
    area = StringField('Area', validators=[DataRequired()])
    location = StringField("Location on Google Maps (URL)", validators=[DataRequired(), URL(message='Invalid URL ')])
    clothes = SelectField("Clothes", choices=["Woman clothes", "Men clothes", "Boy clothes", "Girl clothes", "Baby clothes"], validators=[DataRequired()])
    submit = SubmitField('Submit')

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Signup')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])

# Database Initialization
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Check if the user exists based on the provided email
        user = User.query.filter_by(email=form.email.data).first()

        # If user exists and the password matches the stored hash
        if user and check_password_hash(user.password, form.password.data):
            # Store the user information in session to log them in
            session['user'] = user.email
            flash('Login successful!', 'success')
            return redirect(url_for('info'))  # Redirect to home after login
        else:
            # If email or password is incorrect, flash an error message
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if request.method == 'POST':
        print('Form submitted via POST')
    if form.validate_on_submit():
        print('Form is valid')
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful! Please login.', 'success')
        return redirect(url_for('login'))
    else:
        print('Form validation failed')
        print(form.errors)  # This will print any validation errors.
    return render_template('signup.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/donor', methods=['GET', 'POST'])
def donor():
    if 'user' not in session:
        return redirect(url_for('login'))
    form = DonorForm()
    if form.validate_on_submit():
        new_donor = Donor(
            name=form.name.data, num=form.num.data, state=form.state.data,
            area=form.area.data, location=form.location.data, clothes=form.clothes.data
        )
        db.session.add(new_donor)
        db.session.commit()
        return redirect(url_for('thank_you'))
    return render_template('donor_form.html', form=form)

@app.route('/thank-you')
def thank_you():
    return "Thank you for your donation!"

@app.route('/search')
def search():
    search_clothes = request.args.get('search_clothes', '')
    to_find = Donor.query.filter_by(clothes=search_clothes).all() if search_clothes else []
    return render_template('search_results.html', results=to_find)


@app.route('/info', methods=['GET', 'POST'])
def info():
    if 'user' not in session:
        flash('You must be logged in to access this page.', 'danger')
        return redirect(url_for('login'))

    clothes_types = ["Woman clothes", "Men clothes", "Boy clothes", "Girl clothes", "Baby clothes"]
    states = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
        "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
        "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttarakhand", "Uttar Pradesh",
        "West Bengal", "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Lakshadweep",
        "Delhi", "Puducherry"
    ]

    selected_clothes = []
    selected_state = None

    if request.method == 'POST':
        selected_clothes = request.form.getlist('clothes')  # Get selected clothes types
        selected_state = request.form.get('state')  # Get selected state

        query = Donor.query

        # Filter by selected clothes if any
        if selected_clothes:
            query = query.filter(Donor.clothes.in_(selected_clothes))

        # Filter by selected state if any
        if selected_state:
            query = query.filter(Donor.state == selected_state)

        donors = query.all()
    else:
        donors = Donor.query.all()

    return render_template('info.html', donors=donors, clothes_types=clothes_types, selected_clothes=selected_clothes, states=states, selected_state=selected_state)




if __name__ == '__main__':
    app.run(debug=True)
