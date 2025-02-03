# -*- coding: utf-8 -*-
import re
from pathlib import Path
import pandas as pd
import build_feature_functions
import numpy as np
from tqdm import tqdm
from collections import Counter
import matplotlib.pyplot as plt

'''
Berechnung der Word_frequencies, basierend auf allen Wikipedia Artikeln
'''

input_path = 'parsed_data'
word_counts = Counter()
tqdm.pandas(desc="Processing rows")


for i, csv in tqdm(enumerate(Path(input_path).glob('*'))):
    df = pd.read_csv(csv)
    df['HellParsed'].dropna().progress_apply(
        lambda x: word_counts.update(build_feature_functions.text_to_words(x)))

word_freq_df = pd.DataFrame.from_dict(
    word_counts, orient='index', columns=['Frequency'])
word_freq_df.index.name = 'Word'
word_freq_df = word_freq_df.sort_values(by='Frequency', ascending=False)

word_freq_df.to_csv('feature_data/Word_Frequencies.csv')
