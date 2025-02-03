# -*- coding: utf-8 -*-

import os
import re
import pandas as pd
import numpy as np


def read_documents(folder_path):
    all_lists = []

    # Iteriere durch alle Dateien im Ordner
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)

            # Öffne das Textdokument und lese die Zeilen ein
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

                # Füge die Zeilen zur Liste hinzu
                lines = [line.strip() for line in lines]
                all_lists.append(lines)

    return all_lists


# Rufe die Funktion auf und erhalte die Liste von Listen
result_lists = read_documents('feature_data/Sources')

# Anpassen der Einträge
filter_liste = [' infinitive marker', ' definite article', '/n.', ' n.', '/v.', ' v.', 'adj.', ' adj.', '/adj.', ' number', '/number', 'exclam.',   ' auxiliary',
                ' modal', ' adv.', '/adv.', ' prep.', '/prep.', ' pron.', '/pron.', ',', ' det.', '/det.', ' conj.', '/']
filtered_list_list = []

for liste in result_lists:
    for substring in filter_liste:
        liste = [word.replace(substring, '') for word in liste]
    filtered_list_list.append(liste)

cefr = ["a1", "a2", "b1", "b2", "c1"]


data = {'Vocab': pd.Series(np.concatenate(filtered_list_list)),
        'CEFR': pd.Series([bez for bez, liste in zip(cefr, filtered_list_list) for _ in range(len(liste))])}

df = pd.DataFrame(data)

df['Vocab'] = df['Vocab'].str.replace('\d', '', regex=True)
df['Vocab'] = df['Vocab'].str.replace('\s*\([^)]*\)', '', regex=True)

df = df.drop_duplicates(subset=['Vocab'])
df = df.loc[df['Vocab'] != '']

df.to_csv('feature_data/CEFR/vocab_list.csv')
