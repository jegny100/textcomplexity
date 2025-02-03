# -*- coding: utf-8 -*-
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

feature_folder = 'snippets_with_features'
df_standard = pd.concat([pd.read_csv(file)
                        for file in tqdm(Path(feature_folder).glob('*'))])

feature_folder = 'simple_snippets_with_features'
df_simple = pd.concat([pd.read_csv(file)
                      for file in tqdm(Path(feature_folder).glob('*'))])

df_standard.head()


df_combined = pd.concat([df_standard, df_simple], axis=0)
df_combined = df_combined[['NER', 'a1', 'a2', 'b1', 'b2', 'c1', 'unknown']]
# PCA auf der gesamten Datenmenge durchführen
pca = PCA(n_components=2)
pca_result = pca.fit_transform(df_combined)

# Erstellen eines DataFrames für die Ergebnisse von PCA
df_pca = pd.DataFrame(
    data={'PCA1': pca_result[:, 0], 'PCA2': pca_result[:, 1]})

# Scatterplot erstellen
plt.scatter(df_pca['PCA1'][:len(df_standard)], df_pca['PCA2']
            [:len(df_standard)], color='green', label='df_standard')
plt.scatter(df_pca['PCA1'][len(df_standard):], df_pca['PCA2']
            [len(df_standard):], color='red', label='df_simple')

# Achsentitel und Legende hinzufügen
plt.xlabel('PCA1')
plt.ylabel('PCA2')
plt.legend()
plt.title('Scatterplot nach PCA')

# Plot anzeigen
plt.show()

plt.hist2d(df_pca['PCA1'][:len(df_standard)], df_pca['PCA2']
           [:len(df_standard)], bins=(50, 50), cmap='Blues')
plt.colorbar()

plt.hist2d(df_pca['PCA1'][len(df_standard):], df_pca['PCA2']
           [len(df_standard):], bins=(50, 50), cmap='Blues')
plt.colorbar()

df_pca['PCA2'][len(df_standard):].describe()
df_pca['PCA2'][:len(df_standard)].describe()
