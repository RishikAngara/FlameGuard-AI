from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import os
from werkzeug.utils import secure_filename
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np

# Flask app configuration
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# MySQL database configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",          # Update with your MySQL username
    password="rishik",  # Update with your MySQL password
    database="fgai" # Ensure this database exists
)
cursor = db.cursor()

# Load the trained model
model = tf.keras.models.load_model(r'C:\Users\rishi\OneDrive\Desktop\Amrita\project(resume)\forest fire detection\model\forest_fire_model.h5')
classes = ['fire', 'no fire', 'smoke', 'smoke fire']

# Home route
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('predict'))
    return redirect(url_for('login'))

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username already exists. Please choose another.', 'danger')
            return redirect(url_for('signup'))

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username exists
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user:
            # Username exists, check password
            if user[2] == password:
                session['user_id'] = user[0]
                session['username'] = user[1]
                flash('Login successful!', 'success')
                return redirect(url_for('predict'))
            else:
                flash('Incorrect Password', 'danger')  # If password is wrong
        else:
            flash('User not found', 'danger')  # If username doesn't exist

    return render_template('login.html')


# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

# Prediction route
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user_id' not in session:
        flash('Please log in to access predictions.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            prediction = predict_image(filepath)
            os.remove(filepath)
            return render_template('predict.html', prediction=prediction)

    return render_template('predict.html', prediction=None)

# Prediction function
def predict_image(img_path):
    img = load_img(img_path, target_size=(150, 150))
    img_array = img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    prediction = model.predict(img_array)
    predicted_class = classes[np.argmax(prediction)]
    return predicted_class

if __name__ == '__main__':
    app.run(debug=True)
