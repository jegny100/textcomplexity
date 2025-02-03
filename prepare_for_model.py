# -*- coding: utf-8 -*-
import pandas as pd
from tqdm import tqdm
from pathlib import Path
import joblib
from keras.preprocessing.sequence import pad_sequences


def load_data():
    feature_folder = 'snippets_with_features'
    df_standard = pd.concat([pd.read_csv(file).assign(Quelle=str(file).split('_')[-1])
                            for file in tqdm(Path(feature_folder).glob('*'))])
    df_standard['Label'] = 1

    feature_folder = 'simple_snippets_with_features'
    df_simple = pd.concat([pd.read_csv(file).assign(Quelle=str(file).split('_')[-1])
                          for file in tqdm(Path(feature_folder).glob('*'))])
    df_simple['Label'] = 0

    feature_folder = 'annotated_snippets_with_features'
    df_annotated = pd.concat([pd.read_csv(file).assign(Quelle=str(file).split('_')[-1])
                              for file in tqdm(Path(feature_folder).glob('*'))])
    min_length = min([len(df_simple), len(df_standard), 300000])
    df_combined = pd.concat(
        [df_standard.iloc[:min_length], df_simple.iloc[:min_length]], axis=0)
    # TODO: nochmal analysieren
    df_combined = df_combined.loc[df_combined['max_sent_len'] < 80]
    return df_combined, df_annotated


def prepare_seq(df_combined_seq, folder):
    tokenizer = joblib.load(folder / 'tokenizer.pkl')
    seq_sequences = tokenizer.texts_to_sequences(df_combined_seq['POS'])
    seq_sequences = pad_sequences(seq_sequences)
    return seq_sequences
