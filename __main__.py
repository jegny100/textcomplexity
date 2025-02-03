# -*- coding: utf-8 -*-
import Wiki_Extract_Relevant_CSV_multiple
import parser_trial
import build_dataset
import build_features
import read_annotated_texts
from pathlib import Path

"""
Zentrale Steuerung zur Generierung der Datensätze
 
Mögliche Einstellungen:
    
- Overwrite: 
    True:   Löscht bisherige Daten in den Ordnern erzeugt neue
    False:  Vorhandene generierte Daten werden ergänzt, orientiert sich an der
            Nummerierung der Dateibenennung
            
- Prefixes: Regelt durch Auskommentieren die Steuerung, welche Datenquellen 
            bereinigt und verarbeitet werden sollen
    '': Standard Wikipedia
    'simple_': Simple Wikipedia
    'annotated_' nach GER-Niveaus annotierte Texte für Forschungsfrage 3
    
- Work Steps:   Regelt durch Auskommentieren die Steuerung, 
                welche Verarbeitungsschritte ausgeführt werden sollen 
    'extraction':   Auswahl der interessanten Wikipedia Artikel aus der XML-Datei
    'parsing':      Bereinigung der MediaWiki Texte und parsen in Fließtext
    'snipping':     Letzte Bereinigung der Fließtexte auf Satzebene und 
                    Aufteilung in Snippets 
    'featuring':    Berechnung der Features der Snippets
    
- Snippet Length:   Legt die Anzahl an Sätzen pro Snippet fest
- Articles per file:    Legt die Anzahl an Wikipedia Artikeln fest, 
                        die in eine Datei geschrieben werden sollen
                        
- Max Files:    Legt die maximale Anzahl an zu generierenden Dateien fest
"""

overwrite = True

prefixes = [
<<<<<<< Updated upstream
    #'',
    #'simple_',
=======
    # '',
    'simple_',
>>>>>>> Stashed changes
    'annotated_'
]

work_steps = [
<<<<<<< Updated upstream
    #'extraction',
    #'parsing',
    #'snipping',
=======
    # 'extraction',
    # 'parsing',
    'snipping',
>>>>>>> Stashed changes
    'featuring'
]

snippet_length = 1
articles_per_file = 10000
max_files = 5


for prefix in prefixes:

    if prefix == 'simple_':
        xml_file_path = "wikipedia_dump/simplewiki-latest-pages-articles.xml"
    else:
        xml_file_path = "wikipedia_dump/enwiki-latest-pages-articles.xml"

    # Benennung der Ordner
    raw_folder = prefix + "output_data"
    parsed_folder = prefix + 'parsed_data'
    snippet_folder = prefix + 'snippets'
    feature_folder = prefix + 'snippets_with_features'

    if 'extraction' in work_steps:
        print('Start extracting from wiki dump')
        if prefix == 'annotated_':
            input_path = Path('annotated_data')
            read_annotated_texts.read_cefr_data(input_path, raw_folder)

        else:
            Wiki_Extract_Relevant_CSV_multiple.process_wikipedia_dump(
                xml_file_path, raw_folder, articles_per_file, max_files)
            print('Finished extracting from wiki dump')

    if 'parsing' in work_steps:
        print('Start parsing files')
        parser_trial.parse_files(
            raw_folder, parsed_folder, overwrite, max_files)
        print('Finished parsing files')

    if 'snipping' in work_steps:
        print('Start snipping')
        build_dataset.process_data(
            parsed_folder, snippet_folder, snippet_length, overwrite, max_files)
        print('Finished snipping')

    if 'featuring' in work_steps:
        print('Start adding features')
        build_features.add_features(
            snippet_folder, feature_folder, overwrite, max_files)
        print('Finished adding features')
