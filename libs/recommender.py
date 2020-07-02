import os
import PIL
import subprocess
import numpy as np
from numpy import dot
from numpy.linalg import norm
from sklearn import preprocessing
from libs import spectrogram

from utils import manager
from utils import config


data = None
file_data = 'models/feature.npy'

try:
    data = np.load(file_data)
    filled = True
except FileNotFoundError:
    data = None
    filled = False

num_rank = 5
lb = preprocessing.LabelBinarizer()
lb.fit(['Classical', 'Electronic', 'Folk', 'HipHop', 'Jazz', 'Rock'])

model = None
extract_genre = None
extract_feature = None


def populate_data(filename):
    global data, filled
    try:
        data = np.load(filename)
        filled = True
    except FileNotFoundError:
        data = None
        filled = False


def convert_image_to_array(filename):
    spec = PIL.Image.open(filename).convert('L')
    spec = np.array(spec).astype('float')
    spec = spec / 255
    spec = spec.reshape(spec.shape[0], spec.shape[1], 1)
    return spec


def cos_sim(a, b):
    return dot(a, b)/(norm(a)*norm(b))


def get_recommend(audio, look_genre=False):
    from keras import backend as K
    from keras.models import load_model
    global model, extract_genre, extract_feature
  
    rank = []

    if filled == None: 
        return rank

    if model == None:
        model = load_model('models/spotify.h5')
        extract_genre = K.function(
            [model.layers[0].input], [model.layers[-1].output])
        extract_feature = K.function(
            [model.layers[0].input], [model.layers[-2].output])

    temp_file = 'spec.jpg'
    temp_file = os.path.join(config.temp_directory, temp_file)
    script = os.path.join(os.path.dirname(__file__), 'script.py')
    subprocess.call(['python', script, audio, temp_file])

    spec = convert_image_to_array(temp_file)
    feature = extract_feature([[spec]])[0].reshape(-1)
    genre = extract_genre([[spec]])[0]
    genre = lb.inverse_transform(genre)
    
    print('Predict: {}'.format(genre))
    for item in data:
        rank.append({
            'title': item['title'],
            'artist': item['artist'],
            'duration': item['duration'],
            'source': item['source'],
            'genre': item['genre'],
            'score': cos_sim(item['feature'], feature),
        })

    rank.sort(key=lambda x: x['score'], reverse=True)

    if look_genre:
        rank = list(filter(lambda x: x['genre'] == genre, rank))

    result = rank[1:num_rank+1]
    for i in range(num_rank):
        result[i]['order'] = i

    return result


def generate_data(cb, app):
    script1 = os.path.join(
        os.path.dirname(__file__), 'script_spectrogram.py')
    script2 = os.path.join(
        os.path.dirname(__file__), 'script_feature.py')
    subprocess.call(['python', script1, config.local_directory])

    base_spec = os.path.dirname(os.path.abspath(__file__))
    base_spec = os.path.join(base_spec, '../temp/spectrogram')
    subprocess.call(['python', script2, base_spec, config.local_directory])
    populate_data(file_data)
    cb.cancel()
    app.content.load_setting()