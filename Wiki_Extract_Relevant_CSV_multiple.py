import xml.etree.ElementTree as ET
import csv
import os
import re
from tqdm import tqdm

'''
Funktionen zum Extrahieren der relevanten Wikipedia Artikel und anschließendes 
Speichern in einer CSV

CSV-Format:
    Spalten: ["ID", "Titel", "Text"]

'''


def process_wikipedia_dump(input_path, output_directory, articles_per_file, max_files):
    # Funktion zum Bereinigen der XML-Datei
    # Einlesen der Wikipedia-Dump, filtern der relevanten Informationen
    # und speichern als CSV
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    processed_articles = 0  # Anzahl der bereits verarbeiteten Artikel

    csv_writer = None

    for event, elem in tqdm(ET.iterparse(input_path, events=("start", "end"))):
        if elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}page":
            if event == "end":
                page_id = elem.find(
                    ".//{http://www.mediawiki.org/xml/export-0.10/}id").text
                page_title = elem.find(
                    ".//{http://www.mediawiki.org/xml/export-0.10/}title").text
                page_text = elem.find(
                    ".//{http://www.mediawiki.org/xml/export-0.10/}text").text
                if page_text is not None:

                    if filter_articles(page_title, page_text):

                        # immer wenn csv_writer leer ist oder wir genug Artikel gesammelt haben
                        # Erstelle eine neue Datei
                        if csv_writer is None or processed_articles % articles_per_file == 0:
                            print(processed_articles)
                            # Erstelle eine neue CSV-Datei, wenn die maximale Anzahl erreicht ist
                            if csv_writer:
                                csv_file.close()

                            # Erstelle den Dateinamen
                            file_counter = processed_articles // articles_per_file + 1
                            csv_file_name = f"{output_directory}/output_{file_counter}.csv"

                            # Berücksichtigen der Einstellung zu max. Dateien
                            if file_counter == max_files + 1:
                                break

                            # Öffne die CSV-Datei zum Schreiben
                            csv_file = open(csv_file_name, 'w',
                                            newline='', encoding='utf-8')
                            csv_writer = csv.writer(
                                csv_file, quoting=csv.QUOTE_NONNUMERIC)

                            # Schreibe die Header-Zeile
                            csv_writer.writerow(["ID", "Titel", "Text"])

                        # Schreibe Daten in die CSV-Datei mit Textqualifikationszeichen
                        csv_writer.writerow([page_id, page_title, page_text])

                        processed_articles += 1

                elem.clear()


def filter_articles(title, text):
    # Filtert Artikel anhand diverser Merkmale und gibt als Boolean zurück,
    # ob der Artikel abgespeichert werden soll

    # Wörter, die nicht im Titel oder am Anfang des Textes vorkommen dürfen
    exclude_list = ['redirect', 'wikipedia:', 'category:',
                    "list of", "may refer to", "ambiguation",
                    "template", "mediawiki", 'module:']

    for tabu in exclude_list:
        if tabu in title.lower():
            return False

    for tabu in exclude_list:
        if tabu in text[:50].lower():
            return False

    # wenn im Text mathematische oder chemische Sonderzeichen vorkommen: FALSE
    if ("</math>" in text) or ('</chem>' in text):
        return False

    # Filtern von Texten, die zur Kategorie 'Days of the year' gehören
    if re.search('\[\[category:[^\]]*(days of the year)[^\]]*\]\]', text.lower()):
        return False

    # Filtern von Texten, die zur Kategorie ambig oder stub gehören
    if re.search('\[\[category:[^\]]*(ambig|stub)[^\]]*\]\]', text.lower()):
        return False

    # Filtern von Texten, die gekennzeichnet sind als ambig oder stub
    if re.search('\{\{[^\}]*(ambig|stub)[^\}]*\}\}', text.lower()):
        return False

    # Filtern von Titeln die sich auf Jahre beziehen (z.B. 1890s)
    if re.search('\d\d+s', title.lower()):

        return False

    # wenn der Text den Anforderungen entspricht
    return True
