# -*- coding: utf-8 -*-
import prepare_for_model
from sklearn.model_selection import train_test_split
import joblib
from keras.models import load_model
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from scipy.spatial.distance import jensenshannon
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import pandas as pd
from pathlib import Path


folder = 'FeedForward_1'


features = joblib.load(f'models/{folder}/features.joblib')
features_seq = joblib.load(f'models/{folder}/features_seq.joblib')

df_combined, df_annotated = prepare_for_model.load_data()

if features_seq:
    df_combined = df_combined.loc[df_combined['max_sent_len'] < 128]
    df_annotated = df_annotated.loc[df_annotated['max_sent_len'] < 128]

df_combined_static = df_combined.dropna()[features].astype(float)

df_combined_seq = df_combined.dropna()[features_seq]
# for col in features_seq:
#    df_combined_seq[col] = df_combined_seq[col].str.split('|')
df_combined_label = df_combined.dropna()['Label']

df_annotated_static = df_annotated.dropna()[features].astype(float)

df_annotated_seq = df_annotated.dropna()[features_seq]


scaler = joblib.load(f'models/{folder}/scaler.pkl')
model = load_model(f'models/{folder}/model.h5')

if features and features_seq:

    seq_sequences = prepare_for_model.prepare_seq(
        df_combined_seq, Path(f'models/{folder}'))

    X_static_train, X_static_test, seq_sequences_train, seq_sequences_test, y_train, y_test = train_test_split(
        df_combined_static, seq_sequences, df_combined_label, test_size=0.2, random_state=42)
    X_static_test_scaled = scaler.transform(X_static_test)
    input_test = [seq_sequences_test, X_static_test_scaled]
    X_annotated = df_annotated_static
    X_annotated_scaled = scaler.transform(df_annotated_static)
    seq_sequences_annotated = prepare_for_model.prepare_seq(
        df_annotated_seq,  Path(f'models/{folder}'))
    input_annotated = [seq_sequences_annotated, X_annotated_scaled, ]
elif features:
    X_static_train, X_static_test, y_train, y_test = train_test_split(
        df_combined_static, df_combined_label, test_size=0.2, random_state=42)
    X_static_test_scaled = scaler.transform(X_static_test)
    input_test = [X_static_test_scaled, ]
    X_annotated = df_annotated_static
    X_annotated_scaled = scaler.transform(df_annotated_static)
    input_annotated = [X_annotated_scaled, ]
elif features_seq:
    seq_sequences = prepare_for_model.prepare_seq(df_combined_seq, folder)

    seq_sequences_train, seq_sequences_test, y_train, y_test = train_test_split(
        seq_sequences, df_combined_label, test_size=0.2, random_state=42)
    input_test = [seq_sequences_test]
    seq_sequences_annotated = prepare_for_model.prepare_seq(
        df_annotated_seq, folder)
    input_annotated = [seq_sequences_annotated]


# 4. Modell evaluieren
y_pred = model.predict(input_test)
# y_pred_classes = model.predict_classes([seq_sequences_test, X_static_test_scaled, ])
accuracy = accuracy_score(y_test, y_pred > 0.5)

f1 = f1_score(y_test, y_pred > 0.5)
precision = precision_score(y_test, y_pred > 0.5)
recall = recall_score(y_test, y_pred > 0.5)
print(f'Accuracy: {accuracy * 100:.2f}%')
series_metrics = pd.Series([precision, accuracy, recall, f1], [
                           'precision', 'accuracy', 'recall', 'f1'])
series_metrics.to_csv(f'models/{folder}/test_metriken.csv')

# 5. Grafiken
# Sortieren des Arrays
sorted_data = np.sort(y_pred.flatten())

# Berechnen der kumulativen Verteilung
cumulative = np.linspace(0, 1, len(sorted_data))

# Grafische Darstellung der kumulativen Verteilung
plt.plot(sorted_data, cumulative, linestyle='-', color='b')
plt.xlabel('Vorhersage')
plt.ylabel('Kumulative Verteilung')
plt.title('Kumulative Verteilung der Vorhersagen(Test)')
plt.grid(True)
plt.savefig(f'models/{folder}/Kumulative Verteilung der Vorhersagen(Test).png')
plt.show()
density = gaussian_kde(sorted_data)
density.covariance_factor = lambda: .25
density._compute_covariance()

xs = np.linspace(min(sorted_data), max(sorted_data), 1000)

# Plotten der Dichtefunktion

plt.plot(xs,
         density(xs),  # marker='o',
         linestyle='-')
plt.title('Dichtefunktion der Testdaten')
plt.xlabel('Vorhersage')
plt.ylabel('Dichte')
plt.grid(True)
plt.legend()
plt.savefig(f'models/{folder}/Dichtefunktion der Vorhersagen(Test).png')
plt.show()
# -----------------------------------------------------

#### CEFR ABBILDUNG ####
df_annotated


# df_annotated_small = df_annotated[features].astype(float).dropna()
# df_annotated_small['Label'] = 0


# y_annotated = df_annotated_static['Label']


y_pred_annotated = model.predict(input_annotated)


df_annotated['pred'] = y_pred_annotated
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
plt.figure(figsize=(8, 6))
for i, (title, df_cefr) in enumerate(df_annotated.groupby('Titel')):
    print(df_cefr['pred'].rename(title).describe())
    sorted_data = np.sort(df_cefr['pred'])

    # Berechnen der kumulativen Verteilung
    cumulative = np.linspace(0, 1, len(sorted_data))

    # Grafische Darstellung der kumulativen Verteilung

    plt.plot(sorted_data,
             cumulative,
             marker='o',
             linestyle='-',
             color=colors[i % len(colors)],
             label=title)

    # plt.show()
plt.xlabel('Vorhersage')
plt.ylabel('Kumulative Verteilung')
plt.title('Kumulative Verteilungen der Vorhersagen(Annotated)')
plt.grid(True)
plt.legend()
plt.savefig(
    f'models/{folder}/Kumulative Verteilungen der Vorhersagen(Annotated).png')
bla = df_annotated.groupby('Titel').describe()


colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
density_list = []
plt.figure()
for i, (title, df_cefr) in enumerate(df_annotated.groupby('Titel')):
    density = gaussian_kde(df_cefr['pred'])
    density.covariance_factor = lambda: .25
    density._compute_covariance()
    density_list.append(density)

    xs = np.linspace(0, 1, 1000)

    # Plotten der Dichtefunktion

    plt.plot(xs,
             density(xs),  # marker='o',
             linestyle='-',
             color=colors[i % len(colors)],
             label=title)
    plt.title('Dichtefunktion der Vorhersagen(Annotated)')
    plt.xlabel('Vorhersage')
    plt.ylabel('Dichte')
    plt.grid(True)
    plt.legend()
    # plt.show()
plt.savefig(f'models/{folder}/Dichtefunktion der Vorhersagen(Annotated).png')

df_jensen = pd.DataFrame([[jensenshannon(dens_1(xs), dens_2(xs)) for j, dens_2 in enumerate(density_list)]
                          for i, dens_1 in enumerate(density_list)],
                         index=['a1', 'a2', 'b1', 'b2', 'c1'], columns=['a1', 'a2', 'b1', 'b2', 'c1'])
df_jensen.to_csv(f'models/{folder}/jensenshannon.csv')

level = ['A1', 'A2', 'B1', 'B2', 'C1']

dic = {(level[i], level[j]): [] for i in range(len(density_list))
       for j in range(len(density_list)) if i != j}
for _ in range(1000):
    for i, density in enumerate(density_list):
        sample = density.resample(200)
        likelihood_values = density.evaluate(sample)
        auto_likelihood = np.cumprod(likelihood_values)
        for j, other_density in enumerate(density_list):
            if i != j:
                likelihood_values = other_density.evaluate(sample)
                other_likelihood = np.cumprod(likelihood_values)
                dic[(level[i], level[j])].append(
                    np.argmin((other_likelihood / auto_likelihood) > 0.05)+1)

df_notwendige_ziehungen = pd.DataFrame(dic).describe()
df_notwendige_ziehungen.to_csv(f'models/{folder}/notwendige_ziehungen.csv')
