from flask import Flask, request, jsonify
import torch
import librosa
from flask import render_template
import numpy as np
import matplotlib.pyplot as plt
import librosa.display
import io
import base64
import sys
import os
from datetime import datetime
from flask_mysqldb import MySQL
from cryptography.fernet import Fernet
from Crypto.Random import get_random_bytes
from AES import generate_aes_key, aes_encrypt, aes_decrypt  



sys.path.append('E:/IS')
from train import DeepSonarCNN  # Make sure train.py is in same directory or importable

app = Flask(__name__, template_folder='../ui/UI/Frontend',
                        static_folder='../ui/UI/Frontend/static')

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
prediction_history = []
# Load the model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# model = DeepSonarCNN().to(device)
# model.load_state_dict(torch.load('models/deep_sonar_model2.pth', weights_only=True))
# model.eval()

with open('KEYS/secret.key', 'rb') as key_file:
    secret_key = key_file.read()

fernet = Fernet(secret_key)
with open('models/deepsonarmodel2_encrypted.pth', 'rb') as enc_file:
    encrypted_model_data = enc_file.read()

decrypted_model_data = fernet.decrypt(encrypted_model_data)

# Load the model using torch from a buffer
buffer = io.BytesIO(decrypted_model_data)
model = DeepSonarCNN().to(device)
model.load_state_dict(torch.load(buffer, map_location=device), strict=True)
model.eval()

aes_key = None
with open('KEYS/aes_key.key', 'rb') as key_file:  
    aes_key = key_file.read()
# Preprocessing function
def preprocess_audio(file_path, sr=16000, duration=3, return_signal=False):
    signal, _ = librosa.load(file_path, sr=sr)
    fixed_length = sr * duration
    if len(signal) < fixed_length:
        signal = np.pad(signal, (0, fixed_length - len(signal)))
    else:
        signal = signal[:fixed_length]

    mel_spec = librosa.feature.melspectrogram(y=signal, sr=sr, n_mels=64)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    mel_spec_db = torch.tensor(mel_spec_db).unsqueeze(0).unsqueeze(0).to(device)

    if return_signal:
        return mel_spec_db, signal
    return mel_spec_db
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  
app.config['MYSQL_PASSWORD'] = 'ariba0113' 
app.config['MYSQL_DB'] = 'deepfake_audio' 

mysql = MySQL(app)

@app.route('/')
def signup():
    return render_template('signup.html')  
# @app.route('/')
# def index():
#     return "Deepfake Audio Detection API is Running"
@app.route('/home')
def show_home():
    print("Serving /home route...")
    return render_template('home.html')
@app.route('/login')
def login():
    return render_template('signup.html')

@app.route('/routes')
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote(f"{rule.endpoint:50s} {methods:20s} {str(rule)}")
        output.append(line)
    return "<br>".join(sorted(output))




@app.route('/predict', methods=['POST'])
def predict():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file uploaded'}), 400

    file = request.files['audio']
    filename = file.filename  
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # Read file bytes
    file_bytes = file.read()

    # Encrypt the audio using AES (AES encryption)
    iv, encrypted_audio = aes_encrypt(file_bytes, aes_key)

    # Save the encrypted audio to a file
    encrypted_path = file_path + '.enc'
    with open(encrypted_path, 'wb') as enc_file:
        enc_file.write(encrypted_audio)

    # Decrypt the audio for processing (predicting)
    decrypted_audio = aes_decrypt(encrypted_audio, aes_key, iv)

    # Save the decrypted audio temporarily for librosa to read
    temp_path = file_path + '_temp.wav'
    with open(temp_path, 'wb') as temp_file:
        temp_file.write(decrypted_audio)

    try:
        mel_spec, signal = preprocess_audio(temp_path, return_signal=True)
        with torch.no_grad():
            output = model(mel_spec)
            prediction = (output > 0.5).int()
            label = 'Real' if prediction.item() == 0 else 'Fake'

        # Save history
        prediction_history.append({
            'filename': filename,
            'result': label,
            'date': datetime.now().strftime('%Y-%m-%d')
        })

        # Save in MySQL
        cursor = mysql.connection.cursor()
        query = """INSERT INTO predictions (filename, result, date) 
                   VALUES (%s, %s, %s)"""
        cursor.execute(query, (filename, label, datetime.now().strftime('%Y-%m-%d')))
        mysql.connection.commit()
        cursor.close()

        # Plot waveform + spectrogram
        fig, axs = plt.subplots(1, 2, figsize=(14, 5))

        axs[0].plot(signal, color='dodgerblue')
        axs[0].set_title('Waveform')
        axs[0].set_xlabel('Time')
        axs[0].set_ylabel('Amplitude')
        axs[0].grid(True)

        D = librosa.amplitude_to_db(np.abs(librosa.stft(signal)), ref=np.max)
        img = librosa.display.specshow(D, sr=16000, x_axis='time', y_axis='log', cmap='magma', ax=axs[1])
        axs[1].set_title('Spectrogram')
        fig.colorbar(img, ax=axs[1], format='%+2.0f dB')

        fig.suptitle(f'Prediction: {label}', fontsize=16, color='green' if label == 'Real' else 'red')
        plt.tight_layout(rect=[0, 0, 1, 0.93])

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        plt.close()

        return render_template('results.html', prediction=label, plot_image=img_base64)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/api/predictions')
def get_predictions():
    return jsonify(prediction_history)
# 
@app.route('/admin')
def admin():
    cursor = mysql.connection.cursor()  
    cursor.execute("SELECT * FROM predictions ORDER BY date DESC")
    predictions = cursor.fetchall()
    cursor.close()

    return render_template('admin.html', predictions=predictions)



if __name__ == '__main__':
    
    app.run(debug=True)
