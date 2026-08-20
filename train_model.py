import numpy as np
from sklearn.svm import OneClassSVM
import pickle

# Example dataset (replace with your collected data)
X = np.array([
    [0.12, 0.13],
    [0.11, 0.14],
    [0.10, 0.12],
    [0.13, 0.15]
])

model = OneClassSVM(kernel='rbf', gamma='auto')
model.fit(X)

pickle.dump(model, open("eye_model.pkl", "wb"))

print("Model trained successfully")