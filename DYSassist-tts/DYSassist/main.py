from flask import Flask, render_template, session, redirect, url_for, request, send_from_directory
import sqlite3
import os
from markupsafe import escape
from datetime import timedelta
import logging
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from docx import Document
from gtts import gTTS

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = os.urandom(16)
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=1)
		
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create():
    with sqlite3.connect('login.db') as db:
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS Users(
                        Username text,
                        Password text,
                        Primary Key(Username))
                    """)
        db.commit()
create()

@app.route('/')
def home():
    logger.debug(f"Static folder path: {app.static_folder}")
    logger.debug(f"Static URL path: {app.static_url_path}")
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/add', methods=['POST'])
def add():
    if request.form['psw'] != request.form['confirm_psw']:
        return render_template('signup.html', error="Passwords do not match!")
    
    try:
        with sqlite3.connect('login.db') as db:
            cursor = db.cursor()
            # Check if username already exists
            cursor.execute("SELECT * FROM Users WHERE Username=?", (request.form['uname'],))
            if cursor.fetchone() is not None:
                return render_template('signup.html', error="Username already exists!")
            
            cursor.execute("INSERT INTO Users (Username, Password) VALUES (?,?)",
                         (request.form['uname'], request.form['psw']))
            db.commit()
            return redirect(url_for('login'))
    except Exception as e:
        return render_template('signup.html', error="An error occurred. Please try again.")

@app.route('/verify', methods=['POST'])
def verify():
    with sqlite3.connect('login.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Users WHERE Username=? AND Password=?",
                   (request.form['uname'], request.form['psw']))
        result = cursor.fetchall()
        if len(result) == 0:
            return render_template('index.html', error="Invalid username or password")
        else:
            session.permanent = True
            session['username'] = request.form['uname']
            return redirect(url_for('welcome'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/welcome')
def welcome():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('welcome.html', username=session['username'])

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if 'file' not in request.files:
        return render_template('welcome.html', 
                             username=session['username'], 
                             message='No file selected')
    
    file = request.files['file']
    if file.filename == '':
        return render_template('welcome.html', 
                             username=session['username'], 
                             message='No file selected')
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return render_template('welcome.html', 
                             username=session['username'], 
                             message='File uploaded successfully!',
                             uploaded_file=filename)
    
    return render_template('welcome.html', 
                         username=session['username'], 
                         message='Invalid file type. Only PDF and DOCX files are allowed.')

@app.route('/about')
def about():
    return render_template('about.html')

def read_pdf(file_path):
    """Extract text from PDF file"""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def read_docx(file_path):
    """Extract text from DOCX file"""
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def convert_to_audio(text, output_path):
    """Convert text to audio using gTTS"""
    try:
        tts = gTTS(text=text, lang='en')
        tts.save(output_path)
        return True
    except Exception as e:
        logger.error(f"Error in text-to-speech conversion: {str(e)}")
        return False

@app.route('/convert/<filename>', methods=['POST'])
def convert_to_audiobook(filename):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(file_path):
            return render_template('welcome.html', 
                                username=session['username'], 
                                message='File not found')

        # Create audio folder if it doesn't exist
        audio_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'audio')
        if not os.path.exists(audio_folder):
            os.makedirs(audio_folder)

        # Extract text based on file type
        if filename.endswith('.pdf'):
            text = read_pdf(file_path)
        elif filename.endswith('.docx'):
            text = read_docx(file_path)
        else:
            return render_template('welcome.html', 
                                username=session['username'], 
                                message='Unsupported file type')

        # Convert to audio
        audio_filename = os.path.splitext(filename)[0] + '.mp3'
        audio_path = os.path.join(audio_folder, audio_filename)
        
        if convert_to_audio(text, audio_path):
            return render_template('welcome.html', 
                                username=session['username'],
                                message='Audio conversion successful!',
                                audio_file=audio_filename)
        else:
            return render_template('welcome.html', 
                                username=session['username'],
                                message='Audio conversion failed')

    except Exception as e:
        logger.error(f"Error in conversion: {str(e)}")
        return render_template('welcome.html', 
                            username=session['username'],
                            message='An error occurred during conversion')

@app.route('/audio/<filename>')
def serve_audio(filename):
    if 'username' not in session:
        return redirect(url_for('login'))
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'audio'), filename)

if __name__ == '__main__':
    app.run(debug=True)
