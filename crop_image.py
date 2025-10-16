

import tensorflow as tf, keras
print("Inference TF:", tf.__version__)
print("Inference Keras:", keras.__version__)

model = "Resources/Models/job10001.keras"

model.save("Resources/Models/job10001.h5")