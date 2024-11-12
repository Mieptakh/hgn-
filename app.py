from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school_voting.db'
db = SQLAlchemy(app)

# Models for Users and Votes
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # "student" or "admin"

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(10), nullable=False)  # "female" or "male"

with app.app_context():
    db.create_all()

# Dummy candidates
candidates = {
    'female': ["Bu Andi", "Bu Budi", "Bu Cici"],
    'male': ["Pak Dani", "Pak Eko", "Pak Fajar"]
}

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user'] = username
            session['role'] = user.role
            return redirect(url_for('admin_dashboard' if user.role == 'admin' else 'index'))
        flash("Incorrect username or password")
    return render_template('login.html')

# Admin dashboard for user management and viewing votes
@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash("User added successfully!")
    users = User.query.all()
    votes = Vote.query.all()
    return render_template('admin_dashboard.html', users=users, votes=votes)

# Voting route
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        female_choice = request.form.get('female')
        male_choice = request.form.get('male')
        if female_choice:
            vote = Vote(candidate=female_choice, category='female')
            db.session.add(vote)
        if male_choice:
            vote = Vote(candidate=male_choice, category='male')
            db.session.add(vote)
        db.session.commit()
        flash("Thank you for voting!")
        return redirect(url_for('result'))
    return render_template('index.html', candidates=candidates)

# Route to view results
@app.route('/result')
def result():
    if 'user' not in session:
        return redirect(url_for('login'))
    female_votes = Vote.query.filter_by(category='female').all()
    male_votes = Vote.query.filter_by(category='male').all()
    return render_template('result.html', female_votes=female_votes, male_votes=male_votes)

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
