import os
import sys
import scipy
import glob
import numpy as np
import pandas as pd
import librosa
import librosa.display
import matplotlib.pyplot as plt

from ctypes import c_int
from pydub import AudioSegment
from multiprocessing import Pool, Value


FILE_PATH = os.path.dirname(os.path.abspath(__file__))
DIR_AUDIO = sys.argv[1]
DIR_SPECTOGRAM = os.path.join(FILE_PATH, '../temp/spectrogram')
PROGRESS_FILE = os.path.join(FILE_PATH, '../temp/progress.txt')


def init(current, overall):
    global counter
    global total
    counter = current
    total = overall


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


def log_progress():
    counter.value += 1
    percentage = counter.value * 100 / total.value
    print('Progress: {:.2f}%'.format(percentage), end='\r')
    write_to_file('Generating spectrogram {}/{} ...'.format(counter.value, total.value))


def generate_spectogram(audio, target):
    wav_file = export_to_wav(audio)
    rate, audio = scipy.io.wavfile.read(wav_file)
    remove_file(wav_file)

    S = librosa.feature.melspectrogram(audio[:, 0], sr=rate)
    S = librosa.power_to_db(S, ref_power=np.max)

    setup_plot()
    librosa.display.specshow(S, cmap='gray')
    save_figure(target)

    log_progress()


def generate_spectogram_librosa(audio, target):
    audio, rate = librosa.load(audio)

    S = librosa.feature.melspectrogram(audio, sr=rate)
    S = librosa.power_to_db(S, ref_power=np.max)

    setup_plot()
    librosa.display.specshow(S, cmap='gray')
    save_figure(target)

    log_progress()


def get_file_path(row):
    filename = os.path.basename(row)
    filename = os.path.splitext(filename)[0]

    filename = '{}.png'.format(filename)
    spec_path = os.path.join(DIR_SPECTOGRAM, filename)
    return row, spec_path


def write_to_file(text):
    with open(PROGRESS_FILE, 'w+') as f:
        f.write(text)


def main():
    write_to_file('Starting ...')
    files = glob.glob(os.path.join(DIR_AUDIO, '**/*.mp3'), recursive=True)

    total_unprocessed = len(files)
    print(total_unprocessed)

    current = Value(c_int, 0)
    overall = Value(c_int, total_unprocessed)

    pool = Pool(initializer=init, initargs=(current, overall))

    for row in files:
        filename = os.path.basename(row)
        filename = os.path.splitext(filename)[0]
        audio_path, spec_path = get_file_path(row)
        pool.apply_async(generate_spectogram, (audio_path, spec_path))

    pool.close()
    pool.join()
    write_to_file('Going to next process ...')


if __name__ == '__main__':
    main()
