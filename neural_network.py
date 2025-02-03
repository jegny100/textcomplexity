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
from pathlib import Path
import os

tqdm.pandas(desc="Processing rows")
folder = Path('models/LSTM_1_DEP')
if not os.path.exists(folder):
    os.makedirs(folder)
features = ['word_rarity',
            'max_sent_len',
            'NER',
            'a1', 'a2', 'b1', 'b2', 'c1', 'unknown'
            ]
features_seq = [
    'POS', 'DEP'
]
joblib.dump(features, folder / 'features.joblib')
joblib.dump(features_seq, folder / 'features_seq.joblib')
df_combined, df_annotated = prepare_for_model.load_data()

df_combined_static = df_combined.dropna()[features].astype(float)

df_combined_seq = df_combined.dropna()[features_seq]
# for col in features_seq:
#    df_combined_seq[col] = df_combined_seq[col].str.split('|')
df_combined_label = df_combined.dropna()['Label']

tokenizer = Tokenizer()
tokenizer.fit_on_texts(df_combined_seq['POS'])
joblib.dump(tokenizer, folder / 'tokenizer.pkl')

seq_sequences = prepare_for_model.prepare_seq(df_combined_seq, folder)
word_index = tokenizer.word_index
max_sequence_length = max(len(seq) for seq in seq_sequences)
# Aufteilung in Trainings- und Testdaten
X_static_train, X_static_test, seq_sequences_train, seq_sequences_test, y_train, y_test = train_test_split(
    df_combined_static, seq_sequences, df_combined_label, test_size=0.2, random_state=42)

# Feature Scaling
scaler = StandardScaler()
X_static_train_scaled = scaler.fit_transform(X_static_train)
X_static_test_scaled = scaler.transform(X_static_test)
joblib.dump(scaler, folder / 'scaler.pkl')

# 2. Modell erstellen
seq_input = Input(shape=(max_sequence_length,))
seq_embedding = Embedding(input_dim=len(
    word_index) + 1, output_dim=100, input_length=max_sequence_length)(seq_input)

lstm_out = LSTM(64)(seq_embedding)

static_input = Input(shape=(X_static_train_scaled.shape[1],))
combined = concatenate([lstm_out, static_input])
combined = Dense(64, activation='relu')(combined)
output = Dense(1, activation='sigmoid')(combined)

model = Model(inputs=[seq_input, static_input], outputs=output)

model.compile(loss='binary_crossentropy',
              optimizer='adam', metrics=['accuracy'])

# 3. Modell trainieren
model.fit([seq_sequences_train,
           X_static_train_scaled],
          y_train, epochs=10, batch_size=32,
          validation_data=([seq_sequences_test, X_static_test_scaled], y_test))
model.save(folder / 'model.h5')
# =============================================================================
# model.fit(X_train_scaled, y_train, epochs=20,
#           batch_size=64, validation_split=0.3)
# =============================================================================
