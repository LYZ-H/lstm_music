from lstm.lstm_music import get_train_test_data, init_lstm, load_model, train_model
import os
from midi.read_midi import *

script_dir = os.path.dirname(__file__)

music_list = os.listdir(os.path.join(script_dir, 'midi', 'music'))

music_list.sort(key=lambda ele:int(ele[:-4]))

is_init = False

arr_is_init = False

for music_name in music_list:
    music_path = os.path.join(script_dir, 'midi', 'music', music_name)
    if not arr_is_init:
        total_music_matrix = music_to_matrix(music_path)
        arr_is_init = True
    else:    
        total_music_matrix = np.vstack((total_music_matrix,music_to_matrix(music_path)))

train_test_data = get_train_test_data(total_music_matrix)



model_type = 2

if not is_init:
    model = init_lstm(train_test_data[0], model_type)
    is_init = True
else:
    model = load_model()
    print('model loaded')

train_model(model, train_test_data[0], train_test_data[1])

print('---------------------' + music_name + '-----------------------')






