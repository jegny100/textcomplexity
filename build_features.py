# -*- coding: utf-8 -*-

import pandas as pd
import os
from pathlib import Path
from tqdm import tqdm
from build_feature_functions import ner_calc, geo_mean_prob, max_sent_len, cefr_vocab_calc

'''
Vorbereitung und Berechnung der Features zu den einzelnen Snippets
Es werden CSV Dateien gespeichert 

CSV-Format:
    Spalten: ['Titel', 'Snippet_NR', 'Snippet', 'POS','NER', 'word_rarity',
            'max_sent_len', 'a1', 'a2', 'b1', 'b2', 'c1','unknown', 'Quelle',
            'Label']

'''

tqdm.pandas(desc="Processing rows")




def add_features(snippet_folder, feature_folder, overwrite, max_files):
    feature_folder = Path(feature_folder)
    if not os.path.exists(feature_folder):
        os.makedirs(feature_folder)
    files = [file for file in Path(snippet_folder).glob('*')]
    if overwrite:
        [file.unlink() for file in Path(feature_folder).glob('*')]
    else:
        already_parsed = [str(file).split('_')[-1]
                          for file in Path(feature_folder).glob('*')]
        files = [file for file in files if str(
            file).split('_')[-1] not in already_parsed]

    files = files[:max_files]

    ### KONKRETE BERECHNUNG DER EINZELNEN FEATURES ###
    for i, csv in enumerate(files):
        df_features = pd.read_csv(csv)
        file_ending = str(csv).split('_')[-1]

        spacy_spalten = df_features['Snippet'].progress_apply(
            ner_calc)
        df_features = pd.concat(
            [df_features, spacy_spalten.fillna(0)], axis=1)
        df_features['word_rarity'] = df_features['Snippet'].progress_apply(
            geo_mean_prob)
        df_features['max_sent_len'] = df_features['Snippet'].progress_apply(
            max_sent_len)

        # CEFR Vokabeln
        df_features[['a1', 'a2', 'b1', 'b2', 'c1', 'unknown']] = \
            df_features['Snippet'].progress_apply(
            cefr_vocab_calc).progress_apply(pd.Series)
        df_features.to_csv(
            feature_folder / f'snippets_with_features_{file_ending}', index=True)
