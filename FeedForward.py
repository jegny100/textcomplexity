# -*- coding: utf-8 -*-

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder

from keras.models import Sequential, Model
from keras.layers import Input, LSTM, Dense, Embedding, concatenate, Dropout
from keras.preprocessing.text import Tokenizer

from tqdm import tqdm

import joblib
import prepare_for_model
import os
from pathlib import Path

folder = Path('models/FeedForward_1')
if not os.path.exists(folder):
    os.makedirs(folder)
tqdm.pandas(desc="Processing rows")
features = ['NER',
            'word_rarity',
            'max_sent_len',
            'a1', 'a2', 'b1', 'b2', 'c1', 'unknown'
            ]
features_seq = [
]
joblib.dump(features, folder / 'features.joblib')
joblib.dump(features_seq, folder / 'features_seq.joblib')
df_combined, df_annotated = prepare_for_model.load_data()

df_combined_static = df_combined.dropna()[features].astype(float)


df_combined_label = df_combined.dropna()['Label']


# Aufteilung in Trainings- und Testdaten
X_static_train, X_static_test,  y_train, y_test = train_test_split(
    df_combined_static, df_combined_label, test_size=0.2, random_state=42)

# Feature Scaling
scaler = StandardScaler()
X_static_train_scaled = scaler.fit_transform(X_static_train)
X_static_test_scaled = scaler.transform(X_static_test)
joblib.dump(scaler, folder / 'scaler.pkl')

# 2. Modell erstellen


model = Sequential()
model.add(
    Dense(128, input_dim=X_static_train_scaled.shape[1], activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

# model = Model(inputs=[static_input], outputs=output)

model.compile(loss='binary_crossentropy',
              optimizer='adam', metrics=['accuracy'])

# 3. Modell trainieren
model.fit([X_static_train_scaled],
          y_train, epochs=10, batch_size=32,
          validation_data=([X_static_test_scaled], y_test))
model.save(folder / 'model.h5')
# =============================================================================
# model.fit(X_train_scaled, y_train, epochs=20,
#           batch_size=64, validation_split=0.3)
# =============================================================================
