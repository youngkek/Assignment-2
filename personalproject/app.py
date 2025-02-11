from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('quizzes', lazy=True))

# Create the database tables if they don't exist
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hash the password without specifying the method
        hashed_password = generate_password_hash(password)
        
        # Check if the username already exists
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    quizzes = Quiz.query.filter_by(user_id=session['user_id']).all()
    return render_template('dashboard.html', user=user, quizzes=quizzes)

@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        question = request.form['question']
        answer = request.form['answer']
        new_quiz = Quiz(title=title, question=question, answer=answer, user_id=session['user_id'])
        db.session.add(new_quiz)
        db.session.commit()
        flash('Your quiz has been created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('create_quiz.html')

@app.route('/take_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == 'POST':
        user_answer = request.form['answer']
        is_correct = user_answer.strip().lower() == quiz.answer.strip().lower()
        return render_template('quiz_result.html', is_correct=is_correct, correct_answer=quiz.answer)
    
    return render_template('take_quiz.html', quiz=quiz)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True, port=5002)
