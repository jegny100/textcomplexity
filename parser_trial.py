# -*- coding: utf-8 -*-
import pandas as pd
import mwparserfromhell
import parser_functions
from tqdm import tqdm
from pathlib import Path
import os

'''
Bereinigung der MediaWiki Texte und parsen in Fließtext durch 
den MediaWiki Parser from Hell. 

Angepasst werden dabei in erster Linie Media Syntax Strukturen,
die vom Parser nicht korrekt erkannt werden

Quellen:
    Ben Kurtovic. (o. J.). MWParserFromHell v0.7 Documentation. MWParserFromHell
    Read The Docs. Abgerufen 26. März 2024, von
    https://mwparserfromhell.readthedocs.io/en/latest/
'''

tqdm.pandas(desc="Processing rows")


def parse_files(raw_folder, parsed_folder, overwrite, max_files):
    # Erstellen des Output Ordners und auswählen der Input Dateien
    if not os.path.exists(parsed_folder):
        os.makedirs(parsed_folder)
    files = [file for file in Path(raw_folder).glob('*')]

    if overwrite:
        [file.unlink() for file in Path(parsed_folder).glob('*')]

    else:
        already_parsed = [str(file).split('_')[-1]
                          for file in Path(parsed_folder).glob('*')]
        files = [file for file in files if str(
            file).split('_')[-1] not in already_parsed]

    # Limitieren der zu verarbeitenden Dateien
    files = files[:max_files]

    for i, csv in enumerate(files):
        # Einlesen der kurzen CSV ["ID", "Titel", "Text"]
        csv_str = str(csv)
        filename = csv_str.split('\\')[-1]
        df = pd.read_csv(csv)

        ### ANPASSUNGEN ###

        # Magische Wörter von MediaWiki  entfernen
        print("Magic Words", "\n-------------")
        df['MagicWords'] = df['Text'].str.replace('__[A-Z]+__', '', regex=True)

        # Irrelevante Abschnitte am Ende anhand der Überschrift entfernen
        print('SeeAlso')
        df['SeeAlso'] = df['MagicWords'].progress_apply(
            lambda x: parser_functions.remove_irrelevant_paragraphs(x))

        # alle Überschriften entfernen
        print('Titles', "\n-------------")
        df['Titles'] = df['SeeAlso'].str.replace(
            '=+[^=\r\n]+=+\n', '', regex=True)

        # Category Klammern entfernen
        print('Category', "\n-------------")
        df['Category'] = df['Titles'].str.replace(
            '\[\[Category:[^\]]+\]\]', '', regex=True)

        # [[File: ... ]] entfernen
        print('File')
        df['File'] = df['Category'].progress_apply(
            lambda x: parser_functions.extract_file_parts(x))

        # Wikitables entfernen
        print('WikiTable')
        df['WikiTable'] = df['File'].progress_apply(
            lambda x: parser_functions.extract_wikitable_parts(x))

        # Infoboxen entfernen
        print('Infobox')
        df['Infobox'] = df['WikiTable'].progress_apply(
            lambda x: parser_functions.extract_infobox_parts(x))

        # <ref>-Tags entfernen
        print('Ref', "\n-------------")
        regex1 = r'<ref[^>]*?/>'  # <ref name="auto"/>
        regex2 = r'<ref[^>]*>[\s\S]*?</ref>'  # <ref name=x>{{OED|abjad}}</ref>
        df['Ref'] = df['Infobox'].str.replace(
            fr'{regex1}|{regex2}', '', regex=True)

        # Auflistungen mit Buchzitationen
        print('{{Cite book', "\n-------------")
        df['NoCiteBook'] = df['Ref'].str.replace(
            '\*.*{{[\s\S]*?}}', '* ', regex=True)

        # jegliche Auflistungen entfernen
        print('Listen', "\n-------------")
        df['NoList'] = df['NoCiteBook'].str.replace(
            '\*[^\n]+\n', '', regex=True)

        # von Wiki Markdown zu natürlicher Sprache
        print('HellParsed')
        df['HellParsed'] = df['NoList'].progress_apply(
            lambda x: mwparserfromhell.parse(x).strip_code())

        # übermäßige Leerzeilen entfernen
        # erst nach dem mwparserfromhell
        df['HellParsed'] = df['HellParsed'].str.replace(
            '(\n\s*){1,}', ' ', regex=True)

        # Inhalte innerhalb einfacher Klammern entfernen
        df['HellParsed'] = df['HellParsed'].str.replace(
            '\([^\)|\(]*\)', ' ', regex=True)

        # Doppelte Leerzeichen entfernen
        df['HellParsed'] = df['HellParsed'].str.replace(
            '\s{2,}', ' ', regex=True)

        # verwirrte Kommas entfernen
        df['HellParsed'] = df['HellParsed'].str.replace(
            ',\s+\.', '.', regex=True)

        # CSV Output des DataFrames
        print('to CSV', "\n-------------")
        df[['ID', 'Titel', 'Text', 'HellParsed']].to_csv(
            f"{parsed_folder}/parsed_{filename}", index=False)

        i += 1
        print("DOC ", i)
