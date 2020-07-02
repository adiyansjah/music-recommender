import os
import configparser

# Define config file path
DEFAULT_CONFIG_SRC = 'config.ini'

# Read config file
config = configparser.ConfigParser()
config.read(DEFAULT_CONFIG_SRC)

# Define config's section
folder_config = config['folder']
spotify_config = config['spotify']

local_directory = folder_config.get('local_directory')
temp_directory = folder_config.get('temp_directory')
model_directory = folder_config.get('model_directory')
data_directory = folder_config.get('data_directory')

temp_abs = os.path.basename(os.path.abspath(__file__))
temp_abs = os.path.join(temp_abs, '..')
temp_abs = os.path.join(temp_abs, temp_directory)

client_id = spotify_config.get('client_id')
client_secret = spotify_config.get('client_secret')

def update(loc):
    global local_directory
    with open(DEFAULT_CONFIG_SRC, 'w') as configfile:
        local_directory = loc
        folder_config['local_directory'] = loc
        config.write(configfile)
        