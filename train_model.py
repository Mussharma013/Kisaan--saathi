import os
import numpy as np
from PIL import Image
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from joblib import dump

DATA_DIR = 'data/plantdisease'

X, y = [], []
for label in os.listdir(DATA_DIR):
    folder = os.path.join(DATA_DIR, label)
    if not os.path.isdir(folder):
        continue
    for img_file in os.listdir(folder):
        try:
            img_path = os.path.join(folder, img_file)
            img = Image.open(img_path).convert('L').resize((64, 64))
            X.append(np.array(img).flatten())
            y.append(label)
        except:
            continue

X = np.array(X)
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2)

model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save the model and label encoder
dump(model, 'crop_model.pkl')
dump(label_encoder, 'label_encoder.pkl')

print("✅ Model and label encoder saved.")
