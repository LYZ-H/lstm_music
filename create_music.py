import os
from midi.read_midi import create_music, write_music
predict_result = []
script_dir = os.getcwd()

f = open(os.path.join(script_dir, 'midi', 'music_data', 'data.txt'))
lines = f.readlines()

for line in lines:
    int_arr = []
    line_arr = line[:-1].split(',')
    for val in line_arr:
        int_val = int(float(val))
        if int_val < 0:
            int_val = 0
        int_arr.append(int_val)
    predict_result.append(int_arr)
max_num = 0
for row in predict_result:
    for val in row:
        if val > max_num:
            max_num = val
perc = 120 / max_num        



final_result_get = []
for row in predict_result:
    i_arr = []
    for val in row:
        val *= perc
        i_arr.append(round(val, -1))
    final_result_get.append(i_arr)    

create_music(final_result_get)