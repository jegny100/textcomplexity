# -*- coding: utf-8 -*-

import nltk
import pandas as pd
import re
import numpy as np
from tqdm import tqdm
from pathlib import Path
from nltk.tokenize import sent_tokenize
import spacy

'''
Letzte Bereinigung der Fließtexte auf Satzebene und Aufteilung in Snippets

sentence_filter:    - Splitten die Texte in Sätze und filtert Auslistungen 
                    aufgrund von Kommas und Semikolons
                    - Bündelt die Sätze in Snippets anhand der festgelegten 
                    Länge der main.py
                    
build_snippet_df:   - Strukturiert das DataFrame, sodass eine Zeile nicht mehr 
                    einem Text, sondern einem Snippet entspricht 
                    
process_data:       - Koordiniert, welche Dateien verarbeitet werden
'''

tqdm.pandas(desc="Processing rows")

nltk.download('punkt')
nlp = spacy.load("en_core_web_sm", disable=['tagger', 'parser', 'ner'])
nlp.add_pipe('sentencizer')

def sentence_filter(text, snippet_length):
    # Filtern der Sätze, anhand Histogramm
    sentence_amount = snippet_length
    sentence_list = []
    try:
        # sentence_list = sent_tokenize(text) #NTLK
        doc = nlp(text)
        sentence_list = [sent.text for sent in doc.sents]

        ### Filtern von Sätzen mit Besonderheiten ###
        # Löschen von Sätzen die ein : enthalten
        sentence_list = [x for x in sentence_list if ':' not in x]
        # Löschen von Sätzen die ein ; enthalten
        sentence_list = [x for x in sentence_list if ';' not in x]
        # Löschen von Sätzen mit zu hoher Komma Anzahl
        komma = 8  # -> 99.5 percentil: 8 pro Satz für Beispielset aus 10000 Sätzen
        sentence_list = [x for x in sentence_list if x.count(',') <= komma]

        # Bündeln der Snippets
        snippets_list = [' '.join([sentence_list[i*sentence_amount+j] for j in
                                   range(sentence_amount)])
                         for i in range(len(sentence_list)//sentence_amount)]
    except:
        return []
    return snippets_list


def build_snippet_df(df):
    # Erstelle ein DataFrame, das für jedes Snippet aus der Liste an Snippets
    # eines Wikiartikels eine neue Zeile anlegt und
    # die Snippets pro Artikel durchnummeriert
    return pd.DataFrame([[snippets[1]['Titel'], i, snip] for snippets in df.iterrows()
                         for i, snip in enumerate(snippets[1]['Snippets'])],
                        columns=['Titel', 'Snippet_NR', 'Snippet'])


def process_data(parsed_folder, snippet_folder, snippet_length, overwrite, max_files):
    # Erstellen des Datensatzes
    output_path = Path(snippet_folder)
    if not output_path.exists():
        output_path.mkdir()
    files = [file for file in Path(parsed_folder).glob('*')]
    if overwrite:
        # Löschen aller Dateien
        [file.unlink() for file in Path(snippet_folder).glob('*')]
    else:
        # Auswahl der noch zu bearbeitenden
        already_parsed = [str(file).split('_')[-1]
                          for file in Path(snippet_folder).glob('*')]
        files = [file for file in files if str(
            file).split('_')[-1] not in already_parsed]

    files = files[:max_files]

    snippets_created = 0
    source_texts = 0

    for i, csv in tqdm(enumerate(files)):
        df = pd.read_csv(csv)
        file_ending = str(csv).split('_')[-1]
        # Berechnen der Snippets
        df['Snippets'] = df['HellParsed'].progress_apply(
            lambda x: sentence_filter(x, snippet_length))
        # Erstellen des neuen DataFrames
        df_snippet = build_snippet_df(df)
        snippets_created += len(df_snippet)
        source_texts += len(df)
        # break
        # Speichern des Datensatzes
        df_snippet.to_csv(output_path / f'Snippets_{file_ending}', index=True)
    print(f'{snippets_created} Snippets were created from {i+1} files with {source_texts} texts')