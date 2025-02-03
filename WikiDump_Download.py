import requests
import os
from tqdm import tqdm


# Wikipedia-Dump URL
dump_url = "https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2"

# Wikidumpname
dump_filename = "enwiki-latest-pages-articles.xml.bz2"

# Verzeichnisname
download_directory = "wikipedia_dump"

# Erstellen des Verzeichnisses, wenn es nicht existiert
os.makedirs(download_directory, exist_ok=True)

# Größe des Datenpakets in Bytes
chunk_size = 1024

# bereits heruntergeladene Bytes
downloaded_bytes = 0

# Bestimmen der Dateigröße
response = requests.head(dump_url)
total_size = int(response.headers.get('content-length', 0))

# Einlesen der Wikidump
with open(os.path.join(download_directory, dump_filename), 'wb') as file:

    response = requests.get(dump_url, stream=True)

    # Downloadfortschritt
    with tqdm.wrapattr(file, "write", total=total_size, miniters=1, desc=dump_filename, unit='B', unit_scale=True) as file:
        for data in response.iter_content(chunk_size):
            downloaded_bytes += len(data)
            file.write(data)

print("Download abgeschlossen. Gesamtgröße:", total_size, "Bytes")
