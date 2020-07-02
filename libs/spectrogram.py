import os
import PIL
import scipy
import glob
import numpy as np
import pandas as pd
import librosa
import librosa.display
import matplotlib
import matplotlib.pyplot as plt

from ctypes import c_int
from pydub import AudioSegment


def convert_image_to_array(filename):
    spec = PIL.Image.open(filename).convert('L')
    spec = np.array(spec).astype('float')
    spec = spec / 255
    spec = spec.reshape(spec.shape[0], spec.shape[1], 1)
    return spec


def remove_file(filename):
    os.remove(filename)


def export_to_wav(audio):
    basename, _ = os.path.splitext(audio)
    wav_file = '{}.wav'.format(basename)
    audio = AudioSegment.from_mp3(audio)
    length = len(audio) / 1000
    if length > 30:
        start = ((length/2) - 15) * 1000
        end = ((length/2) + 15) * 1000
        audio = audio[start:end]
    audio.export(wav_file, format='wav')
    return wav_file


def setup_plot():
    plt.figure(figsize=(20, 1.25))


def save_figure(target):
    plt.savefig(target, bbox_inches='tight', pad_inches=-0.05)
    plt.close()


def generate_spectogram(audio, target):
    wav_file = export_to_wav(audio)
    rate, audio = scipy.io.wavfile.read(wav_file)
    remove_file(wav_file)

    S = librosa.feature.melspectrogram(audio[:,0], sr=rate)
    S = librosa.power_to_db(S, ref_power=np.max)

    setup_plot()
    librosa.display.specshow(S, cmap='gray')
    save_figure(target)

    return target


        
