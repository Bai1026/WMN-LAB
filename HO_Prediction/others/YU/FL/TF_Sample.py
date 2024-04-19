import tensorflow as tf
import tensorflow_federated as tff

# Load simulation data.
source, _ = tff.simulation.datasets.emnist.load_data()


def client_data(n):
    return source.create_tf_dataset_for_client(source.client_ids[n]).map(
        lambda e: (tf.reshape(e['pixels'], [-1]), e['label'])
    ).repeat(10).batch(20)


# Pick a subset of client devices to participate in training.
train_data = [client_data(n) for n in range(3)]
print(train_data[0])
it = train_data[0].__iter__()
for nb in it:
    print(nb)
# Wrap a Keras model for use with TFF.


def model_fn():
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(10, tf.nn.softmax, input_shape=(784,),
                              kernel_initializer='zeros')
    ])
    print(train_data[0].element_spec)
    return tff.learning.models.from_keras_model(
        model,
        input_spec=train_data[0].element_spec,
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=[tf.keras.metrics.SparseCategoricalAccuracy()])

# model_fn()
# Simulate a few rounds of training with the selected client devices.
trainer = tff.learning.algorithms.build_weighted_fed_avg(
    model_fn,
    client_optimizer_fn=lambda: tf.keras.optimizers.SGD(0.1))
state = trainer.initialize()
for _ in range(5):
    state, metrics = trainer.next(state, train_data)
    print(state)
    # print(metrics)
