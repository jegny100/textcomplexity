# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path
import os

'''
Einlesen der GER-annotierten Texte des British Council und speicher als DataFrame
Spalten: ID, Titel (Sprachlevel), Text

Quelle:
    British Council. (o. J.). Reading. Reading | English. Abgerufen 26. März 2024,
    von https://learnenglish.britishcouncil.org/skills/reading
'''


def read_cefr_data(input_path, output_path):
    output_path = Path(output_path)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for file in input_path.glob('*'):
        with open(file, 'r') as datei:
            text = datei.read()
        level = str(file).split('.')[0][-2:]
        df = pd.DataFrame([[0, level, text]], columns=["ID", "Titel", "Text"])
        df.to_csv(output_path / f'output_{level}.csv')
