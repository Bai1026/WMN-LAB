import tensorflow as tf
import tensorflow_federated as tff
import numpy as np
import pandas as pd
from tqdm import tqdm
import os
import random
import collections

# Parameters
N_CLIENTS = 5
N_EPOCHS = 20
BATCH_SIZE = 20
TIME_SEQ = 20
SHUFFLE_BUFFER = 10
PREFETCH_BUFFER = 100
OPERATION = 'regression'

dirname = '/home/wmnlab/Documents/sheng-ru/HO-Prediction/data/single'
dirlist = os.listdir(dirname)

# Modify model here


# def create_keras_model():
#     return tf.keras.models.Sequential([
#         tf.keras.layers.Embedding(input_dim=320, output_dim=64),
#         tf.keras.layers.LSTM(128),
#         tf.keras.layers.Dense(1, tf.nn.relu)])
    
def create_keras_model():
    return tf.keras.models.Sequential([
        tf.keras.layers.Dense(240, tf.nn.softmax, input_dim=320),
        tf.keras.layers.Dense(128, tf.nn.softmax),
        tf.keras.layers.Dense(1, tf.nn.softmax)])


def client_dataset_create(dir_name, dir_list):
    def ts_array_create(dirname, dir_list, time_seq):
        features = ['LTE_HO', 'MN_HO', 'eNB_to_ENDC', 'gNB_Rel', 'gNB_HO', 'RLF', 'SCG_RLF',
                    'num_of_neis', 'RSRP', 'RSRQ', 'RSRP1', 'RSRQ1', 'nr-RSRP', 'nr-RSRQ', 'nr-RSRP1', 'nr-RSRQ1']
        target = ['LTE_HO', 'MN_HO']
        split_time = []
        for i, f in enumerate(tqdm(dir_list)):
            f = os.path.join(dirname, f)
            df = pd.read_csv(f)

            # preprocess data with ffill method
            del df['Timestamp'], df['lat'], df['long'], df['gpsspeed']

            X = df[features]
            Y = df[target]

            Xt_list = []

            for j in range(time_seq):
                X_t = X.shift(periods=-j)
                Xt_list.append(X_t)

            X_ts = np.array(Xt_list)
            X_ts = np.transpose(X_ts, (1, 0, 2))
            X_ts = X_ts[:-(time_seq), :, :]
            X_ts = X_ts.reshape(-1, 320)

            Y = Y.to_numpy()
            Y = [1 if sum(y) > 0 else 0 for y in Y]

            YY = []

            for j in range(time_seq, len(Y)):
                count = 0
                for k in range(j, len(Y)):
                    count += 1
                    if Y[k] != 0:
                        break
                YY.append(1 if count <= 20 else 0)

            # YY = np.array(YY).reshape(-1, 1)

            split_time.append(len(X_ts))

            if i == 0:
                X_final = X_ts
                Y_final = YY
            else:
                X_final = np.concatenate((X_final, X_ts), axis=0)
                Y_final = np.concatenate((Y_final, YY), axis=0)
        split_time = [(sum(split_time[:i]), sum(split_time[:i])+x)
                      for i, x in enumerate(split_time)]
        return X_final, Y_final,  split_time

    train_measurements, train_labels, train_time = ts_array_create(
        dir_name, dir_list, time_seq=TIME_SEQ)
    # Make Dataset
    train_dataset = tf.data.Dataset.from_tensor_slices((train_measurements, train_labels)).repeat(
        N_EPOCHS).shuffle(SHUFFLE_BUFFER, seed=1).batch(BATCH_SIZE).prefetch(PREFETCH_BUFFER)

    return train_dataset


dirlists = []
for _ in range(N_CLIENTS):
    dirlists.append([])
for dn in dirlist:
    tmp = random.randint(0, N_CLIENTS - 1)
    for i in range(tmp + 1):
        dirlists[i].append(dn)

federated_dataset = []
for dlst in dirlists:
    federated_dataset.append(client_dataset_create(dirname, dlst))


def model_fn():
    # We _must_ create a new model here, and _not_ capture it from an external
    # scope. TFF will call this within different graph contexts.
    keras_model = create_keras_model()
    # print(federated_dataset[0].element_spec)
    return tff.learning.models.from_keras_model(
        keras_model,
        input_spec=federated_dataset[0].element_spec,
        loss=tf.keras.losses.MeanAbsoluteError(),
        metrics=[tf.keras.metrics.MeanAbsoluteError()])


training_process = tff.learning.algorithms.build_unweighted_fed_avg(
    model_fn,
    client_optimizer_fn=lambda: tf.keras.optimizers.SGD(learning_rate=0.02),
    server_optimizer_fn=lambda: tf.keras.optimizers.SGD(learning_rate=0.1))

state = training_process.initialize()
evaluation = tff.learning.build_federated_evaluation(model_fn)
# result = training_process.next(train_state, federated_dataset)
# train_state = result.state
# train_metrics = result.metrics
# print('round  1, metrics={}'.format(train_metrics))
for round_num in range(N_EPOCHS):
    state, metrics = training_process.next(state, federated_dataset)
    print('round {:2d}, metrics={}'.format(round_num, metrics))
