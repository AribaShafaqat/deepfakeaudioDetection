

import os
import torch
import librosa
import numpy as np
from torch.utils.data import Dataset

class AudioDataset(Dataset):
    def __init__(self, sr=16000, duration=3):
        self.data = []
        self.labels = []
        self.sr = sr
        self.duration = duration
        self.fixed_length = sr * duration

        root_dir = 'E:\\IS\\data\\for-norm\\training'  # Corrected path here

        for label, folder in enumerate(['real', 'fake']):
            folder_path = os.path.join(root_dir, folder)
            for file in os.listdir(folder_path):
                if file.endswith('.wav'):
                    self.data.append(os.path.join(folder_path, file))
                    self.labels.append(label)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        file_path = self.data[idx]
        label = self.labels[idx]
        signal, _ = librosa.load(file_path, sr=self.sr)

        # Pad or cut to fixed length
        if len(signal) < self.fixed_length:
            pad_width = self.fixed_length - len(signal)
            signal = np.pad(signal, (0, pad_width))
        else:
            signal = signal[:self.fixed_length]

        # Convert to Mel Spectrogram
        mel_spec = librosa.feature.melspectrogram(y=signal, sr=self.sr, n_mels=64)

        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

        mel_spec_db = torch.tensor(mel_spec_db).unsqueeze(0)  # Add channel dimension
        label = torch.tensor(label)

        return mel_spec_db, label