import os
import numpy as np
import keras
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import CuDNNLSTM
from keras.layers import Bidirectional
from numpy.random import seed
from tensorflow import set_random_seed
from sklearn.preprocessing import normalize

seed(1)
set_random_seed(1)
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

n_timestamp = 72
n_epochs = 5000
filter_on = 1

script_dir = os.path.dirname(__file__)

def get_train_test_data(music_matrix):
    data_length = len(music_matrix)
    train_length = int(data_length*2/3)
    x_train = []
    y_train = []
    x_test = []
    y_test = []
    for i in range(train_length-n_timestamp):
        x_train.append(music_matrix[i:i+n_timestamp])
        y_train.append(music_matrix[i+n_timestamp+1])

    for i in range(train_length-n_timestamp-1, data_length-n_timestamp-1):
        x_test.append(music_matrix[i:i+n_timestamp])
        y_test.append(music_matrix[i+n_timestamp+1])

    x_train = np.array(x_train)
    y_train = np.array(y_train)
    x_test = np.array(x_test)
    y_test = np.array(y_test)
    return [x_train, y_train, x_test, y_test]



def init_lstm(x_train, model_type):
    model = None
    if model_type == 1:
        # Single cell LSTM
        model = Sequential()
        model.add(CuDNNLSTM(units = 50, activation='relu',input_shape = (x_train.shape[1], 1)))
        model.add(Dense(units = 1))
    if model_type == 2:
        # Stacked LSTM
        model = Sequential()
        model.add(CuDNNLSTM(128, return_sequences=True, input_shape=(x_train.shape[1], 128)))
        model.add(CuDNNLSTM(128, return_sequences=True, input_shape=(x_train.shape[1], 128)))
        model.add(CuDNNLSTM(128))
        model.add(Dense(128))
    if model_type == 3:
        # Bidirectional LSTM
        model = Sequential()
        model.add(Bidirectional(CuDNNLSTM(50, activation='relu'), input_shape=(x_train.shape[1], 1)))
        model.add(Dense(1))
    return model    


def load_model():
    return keras.models.load_model(os.path.join(script_dir, 'model', 'model.h5'))

def predict_model_liter(model, init_data):

    # a = [0] * 128
    # a[64] = 0.9
    # a[32] = 0.9
    # predict_matrix = np.array([[a]*n_timestamp])
    predict_matrix = np.array([init_data])

    total_matrix = np.array([[[0] * 128]])
    for i in range(3000):
        y_predicted = model.predict(predict_matrix)
        predict_matrix = np.array([np.vstack((predict_matrix[:,1:,:][0], y_predicted[0]))])
        total_matrix = np.array([np.vstack((total_matrix[0], y_predicted[0]))])  
    result = []


    max_num = 0
    for row in total_matrix[0]:
        for val in row:
            if val > max_num:
                max_num = val
    perc = 120 / max_num
    print(max_num)
    for row in total_matrix[0]:
        row_arr = []

        for val in row:
            val *= perc
            if val < 0:
                val = 0
            row_arr.append(round(val, -1))
        result.append(row_arr)   
    return result

def train_model(model, x_train, y_train):
    opt = keras.optimizers.Adam(lr=0.005)
    model.compile(optimizer = opt, loss = 'mean_squared_error')
    model.fit(x_train, y_train, epochs = n_epochs, batch_size = 8388608)
    model.save(os.path.join(script_dir, 'model', 'model.h5'))


def predict_model_test(model, x_test):
    y_predicted = model.predict(x_test).tolist()
    result = []

    for row in y_predicted:
        row_arr = []
        for val in row:
            value *= 2
            value = round(val)
            if value < 0:
                value = 0
            row_arr.append(round(value, -1))
        result.append(row_arr)   

    return result    
