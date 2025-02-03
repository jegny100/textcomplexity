Alle Ergebnisse der in der Masterarbeit verwendeten Modelle sind im Ordner "models" gespeichert. 

# Anleitung

Aufgrund von Versionskonflikten verschiedener Python Bibliotheken werden unterschiedliche Entwicklungsumgebungen für einzelne Programmschritte verwendet.

1. Aktivierung der Umgebung 'MASTER'
2. Download der Wikipedia Dumps mit der Datei 'WikiDump_Download.py'
3. Manuelles entpacken der WikiDumps
4. Ausführen der Datei '__main__.py', um die Daten zu generieren, bereinigen und die Features zu berechnen
    - Einstellungsmöglichkeiten zur Anzahl an zu erstellenden Datensätze und Snippetlängen
5. Aktivierung der Umgebung 'MASTER_NN'
6. Ausführen von 'FeedForward.py' zum trainieren eines Feed Forward Modells
    - Setzen eines Ordnernamens, um bereits existierende Modelle nicht zu überschreiben
7. Ausführen von 'neural_network.py' zum trainieren eines LSTM Modells
    - Setzen eines Ordnernamens, um bereits existierende Modelle nicht zu überschreiben
8. Auswerten der Modelle mit 'neural_network_auswertung.py'
    - Eintragen des Ordners, des Modells, das analysiert werden soll
