from lstm.lstm_music import load_model, predict_model_liter, get_train_test_data
from midi.read_midi import *

script_dir = os.path.dirname(__file__)

music_list = os.listdir(os.path.join(script_dir, 'midi', 'music'))

music_list.sort(key=lambda ele:int(ele[:-4]))

arr_is_init = False

for music_name in music_list:
    music_path = os.path.join(script_dir, 'midi', 'music', music_name)
    if not arr_is_init:
        total_music_matrix = music_to_matrix(music_path)
        arr_is_init = True
    else:    
        total_music_matrix = np.vstack((total_music_matrix,music_to_matrix(music_path)))

train_test_data = get_train_test_data(total_music_matrix)
model = load_model()
predict_result = predict_model_liter(model, train_test_data[2][0])
print('predicted')
create_music(predict_result)
write_music(predict_result)
print('music created')





