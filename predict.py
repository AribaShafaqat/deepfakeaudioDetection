import torch
import librosa
import numpy as np
import matplotlib.pyplot as plt
import librosa.display  # Add this for better spectrogram plotting
from train import DeepSonarCNN  # Import your model

# Load the model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = DeepSonarCNN().to(device)
model.load_state_dict(torch.load('models/deep_sonar_model.pth',weights_only=True)) 
model.eval()

# Preprocess the audio
def preprocess_audio(file_path, sr=16000, duration=3):
    signal, _ = librosa.load(file_path, sr=sr)

    # Pad or cut
    fixed_length = sr * duration
    if len(signal) < fixed_length:
        pad_width = fixed_length - len(signal)
        signal = np.pad(signal, (0, pad_width))
    else:
        signal = signal[:fixed_length]

    # Mel-Spectrogram for model input
    mel_spec = librosa.feature.melspectrogram(y=signal, sr=sr, n_mels=64)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

    mel_spec_db = torch.tensor(mel_spec_db).unsqueeze(0).unsqueeze(0)  # batch, channel
    return mel_spec_db.to(device), signal

#Predict and plot both Waveform and Spectrogram
def predict_and_plot(file_path):
    mel_spec_db, signal = preprocess_audio(file_path)

    with torch.no_grad():
        output = model(mel_spec_db)
        prediction = (output > 0.5).int()
        label = 'Real' if prediction.item() == 0 else 'Fake'

    # Plot
    plt.figure(figsize=(14, 5))

    # Waveform
    plt.subplot(1, 2, 1)
    plt.plot(signal, color='dodgerblue')
    plt.title('Waveform')
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.grid(True)

    # Spectrogram
    plt.subplot(1, 2, 2)
    D = librosa.amplitude_to_db(np.abs(librosa.stft(signal)), ref=np.max)
    librosa.display.specshow(D, sr=16000, x_axis='time', y_axis='log', cmap='magma')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram')

    # Main Title
    plt.suptitle(f'Prediction: {label}', fontsize=16, color='green' if label == 'Real' else 'red')

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plt.show()

    return label

# Example Usage
if __name__ == '__main__':
    unseen_audio_path = r'E:\IS\data\for-original\for-original\testing\real\file7.wav'
    prediction = predict_and_plot(unseen_audio_path)
    print(f"The predicted label for the audio is: {prediction}")
