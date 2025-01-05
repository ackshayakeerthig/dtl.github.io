from flask import Flask, render_template, redirect, url_for, request, session, flash
import random
import string
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, URL, Length, ValidationError, Email, EqualTo,InputRequired,Optional
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from urllib.parse import urlparse, urljoin
from functools import wraps
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
    username = db.Column(db.String(80), unique=True, nullable=False)  # Added username
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Added category
    phone_number = db.Column(db.String(15))  # Added phone_number (optional)

    def __repr__(self):
        return f"<User {self.username}>"

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
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    category = SelectField('Category', choices=[
        ('individual', 'Individual'),
        ('orphanage', 'Orphanage'),
        ('fashiondesigner', 'Fashion Designer')
    ], validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[Optional(), Length(min=10, max=15)])
    submit = SubmitField('Signup')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])
    
# Database Initialization
with app.app_context():
    db.create_all()
def is_safe_url(target):
    """
    Ensure the target URL is safe to redirect to (prevents open redirect vulnerabilities).
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc
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
            # Store the user's email and ID in the session
            session['user'] = {
                'email': user.email,
                'id': user.id
            }
            flash('Login successful!', 'success')

            # Redirect to the originally requested page (if any)
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            else:
                # Redirect to a default page if 'next' is not provided or unsafe
                return redirect(url_for('home'))  # Change 'home' to your desired default page
        else:
            # If email or password is incorrect, flash an error message
            flash('Invalid email or password', 'danger')
    
    # Store the 'next' parameter in the template context
    next_page = request.args.get('next')
    return render_template('login.html', form=form, next=next_page)







@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if request.method == 'POST':
        print('Form submitted via POST')
        if form.validate_on_submit():
            print('Form is valid')
            # Hash the password
            hashed_password = generate_password_hash(form.password.data)
            # Create a new user with all fields
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_password,
                category=form.category.data,
                phone_number=form.phone_number.data
            )
            # Add and commit the new user to the database
            db.session.add(new_user)
            db.session.commit()
            flash('Signup successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            print('Form validation failed')
            print(form.errors)  # Print validation errors for debugging
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
    # List of sustainability or donation-related quotes
    quotes = [
        "Thank you for your donation! Together, we can make the world a better place.",
        "Your generosity helps us move towards a more sustainable future.",
        "Every donation counts. Thank you for making a difference!",
        "The Earth thanks you for your contribution to a greener tomorrow.",
        "Your kindness is the seed for a better future. Thank you!",
    ]

    # Select a random quote
    random_quote = random.choice(quotes)

    # Render the thank you page with the random quote
    return render_template('thank_you.html', quote=random_quote)

@app.route('/chat/<int:user_id>', methods=['GET'])
def chat(user_id):
    if 'user' not in session:
        flash('You must be logged in to access this page.', 'danger')
        return redirect(url_for('login'))

    # Fetch the logged-in user
    logged_in_user = User.query.filter_by(id=session['user']['id']).first()
    if not logged_in_user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    # Fetch the other user (individual or fashion designer)
    other_user = User.query.get(user_id)
    if not other_user:
        flash('User not found.', 'danger')
        return redirect(url_for('messages'))

    # Fetch chat history between the logged-in user and the other user
    chat_history = ChatMessage.query.filter(
        ((ChatMessage.sender_id == logged_in_user.id) & (ChatMessage.receiver_id == user_id)) |
        ((ChatMessage.sender_id == user_id) & (ChatMessage.receiver_id == logged_in_user.id))
    ).order_by(ChatMessage.timestamp).all()

    return render_template('chat.html', other_user=other_user, chat_history=chat_history, logged_in_user=logged_in_user)




@app.route('/messages')
def messages():
    if 'user' not in session:
        flash('You must be logged in to access this page.', 'danger')
        return redirect(url_for('login'))

    # Fetch the logged-in user
    user = User.query.filter_by(id=session['user']['id']).first()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    # Fetch users the logged-in user has chatted with
    sent_messages = ChatMessage.query.filter_by(sender_id=user.id).all()
    received_messages = ChatMessage.query.filter_by(receiver_id=user.id).all()

    # Combine and deduplicate users
    users_chatted_with = set()
    for message in sent_messages:
        users_chatted_with.add(message.receiver)
    for message in received_messages:
        users_chatted_with.add(message.sender)

    return render_template('messages.html', users_chatted_with=users_chatted_with)


@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user' not in session:
        flash('You must be logged in to send messages.', 'danger')
        return redirect(url_for('login'))

    # Get form data
    receiver_id = request.form.get('receiver_id')
    message = request.form.get('message')

    if not receiver_id or not message:
        flash('Invalid request.', 'danger')
        return redirect(url_for('messages'))

    # Fetch the logged-in user
    logged_in_user = User.query.filter_by(id=session['user']['id']).first()
    if not logged_in_user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    # Save the message to the database
    new_message = ChatMessage(
        sender_id=logged_in_user.id,
        receiver_id=receiver_id,
        message=message
    )
    db.session.add(new_message)
    db.session.commit()

    flash('Message sent successfully!', 'success')
    return redirect(url_for('chat', user_id=receiver_id))




@app.route('/search')
def search():
    search_clothes = request.args.get('search_clothes', '')
    to_find = Donor.query.filter_by(clothes=search_clothes).all() if search_clothes else []
    return render_template('search_results.html', results=to_find)

@app.route('/fashiondesigners')
def fashiondesigners():
    if 'user' not in session:
        flash('You must be logged in to access this page.', 'danger')
        return redirect(url_for('login'))

    # Fetch all users with the category 'fashiondesigner'
    fashion_designers = User.query.filter_by(category='fashiondesigner').all()
    return render_template('fashiondesigners.html', fashion_designers=fashion_designers)

   
@app.route('/info', methods=['GET', 'POST'])
def info():
    # Check if the user is logged in
    if 'user' not in session:
        flash('You must be logged in to access this page.', 'danger')
        return redirect(url_for('login'))

    # Fetch the logged-in user
    user = User.query.filter_by(id=session['user']['id']).first()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    # Check if the user belongs to the 'orphanage' category
    if user.category != 'orphanage':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))  # Redirect to home or another appropriate page

    # Proceed with the rest of the logic for the /info route
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
