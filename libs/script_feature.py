import os
import PIL
import csv
import sys
import math
import glob
import time
import numpy as np
from mutagen.mp3 import EasyMP3
from keras import backend as K
from keras.models import load_model
from sklearn import preprocessing


FILE_PATH = os.path.dirname(os.path.abspath(__file__))
PROGRESS_FILE = os.path.join(FILE_PATH, '../temp/progress.txt')
SAVE_FILE = os.path.join(FILE_PATH, '../models/feature.npy')

spec_folder = sys.argv[1]
music_folder = sys.argv[2]

feature_test = []
spec_list = glob.glob(os.path.join(spec_folder, '*'))
music_list = glob.glob(os.path.join(music_folder, '**/*.mp3'), recursive=True)

base = os.path.basename(os.path.abspath(__file__))
model = load_model(os.path.join(base, '../models/spotify.h5'))

extract_genre =  K.function([model.layers[0].input], [model.layers[-1].output])
extract_feature =  K.function([model.layers[0].input], [model.layers[-2].output])

lb = preprocessing.LabelBinarizer()
lb.fit(['Classical', 'Electronic', 'Folk', 'HipHop', 'Jazz', 'Rock'])

total = len(spec_list)


def track_info(spec):
    spec = os.path.basename(spec)[:-4]
    print(spec)
    print(music_list)
    for item in music_list:
        base = os.path.basename(item)
        base = base[:-4]
        print(base)
        if base == spec:
            return item


def convert_image_to_array(filename):
    spec = PIL.Image.open(filename).convert('L')
    spec = np.array(spec).astype('float')
    spec = spec / 255
    spec = spec.reshape(spec.shape[0], spec.shape[1], 1)
    return spec


def write_to_file(text):
    with open(PROGRESS_FILE, 'w+') as f:
        f.write(text)

write_to_file('Starting feature extraction ...')


for i, item in enumerate(spec_list):
    val = convert_image_to_array(item)
    track = track_info(item)
    print(item)
    audio = EasyMP3(track)
    feature_test.append({
        'feature': extract_feature([[val]])[0].reshape(-1),
        'genre': lb.inverse_transform(extract_genre([[val]])[0]),
        'title': ', '.join(audio.get('title', ['Unknown'])),
        'artist':', '.join(audio.get('artist', ['Unknown'])),
        'duration': int(audio.info.length),
        'source': track
    })

    print('Extracting feature {}/{} ...'.format(i+1, total))
    write_to_file('Extracting feature {}/{} ...'.format(i+1, total))
    

write_to_file('Finishing ...')
np.save(SAVE_FILE, feature_test)
for item in spec_list: os.remove(item)
time.sleep(1)
os.remove(PROGRESS_FILE)