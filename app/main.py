from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import tensorflow as tf
from PIL import Image
import numpy as np
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_model():
    model_path = 'models/model.h5'
    model = tf.keras.models.load_model(model_path)
    return model

model = load_model()

def predict_image(file_path):
    try:
        image = Image.open(file_path)
        image = image.resize((150, 150))  # Sesuaikan dengan ukuran input model Anda
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)
        
        predictions = model.predict(image_array)
        
        # Menggunakan argmax untuk mendapatkan indeks kelas dengan nilai probabilitas tertinggi
        predicted_class_index = np.argmax(predictions, axis=1)[0]

        # Menyusun daftar label kelas yang sesuai dengan output model Anda
        class_labels = ['Paper','Rock', 'Scissor']

        # Mendapatkan label dan probabilitas hasil prediksi
        prediction_label = class_labels[predicted_class_index]
        accuracy = predictions[0][predicted_class_index]

        return prediction_label, accuracy, None

    except Exception as e:
        print(f"Error during prediction: {e}")
        return "Error", None, str(e)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('home'))

    file = request.files['file']

    if file.filename == '':
        return redirect(url_for('home'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        prediction_label, accuracy, time_taken = predict_image(file_path)

        return render_template('index.html', prediction_label=prediction_label, accuracy=accuracy, time_taken=time_taken, filename=filename)

    else:
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
