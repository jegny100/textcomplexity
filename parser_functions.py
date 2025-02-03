# -*- coding: utf-8 -*-

import re

'''
Sammlung an unterstützenden Funktionen zur Bereinigung der Texte
'''


def extract_file_parts(text):
    ''' 
    Löschen der [[File: ... ]] Teile im Text
    Return: gefilterter String (Text)
    '''
    result = []
    stack = []
    current_part = ''

    for char in text:
        current_part += char

        if char == '[':
            stack.append('[')
        elif char == ']':
            if stack:
                stack.pop()
            else:
                # Wenn die schließende Klammer keine passende öffnende Klammer hat
                current_part = ''

        if not stack:
            # Wenn die äußerste Klammer erreicht wurde
            if current_part.startswith('[[File:'):
                result.append(current_part.strip())
            current_part = ''

    for match in result:
        text = text.replace(match, '')

    return text


def extract_wikitable_parts(text):
    '''
    Sucht nach allen WikiTables im String 'text' und entfernt diese
    Return: gefilterter Text
    '''

    indices = collect_indices(text.lower(), "wikitable")

    # Iteriere rückwärts durch die Indize Liste, um bei jedem Löschen, die Position nicht neu berechnen zu müssen
    for table_index in indices[::-1]:

        # Suche nach "class" VOR "wikitable"
        class_index = text.rfind("class", max(
            0, table_index - 20), table_index)

        # Wenn keine Class vorhanden ist, unveränderter Text
        if class_index == -1:
            continue

        # Suche nach der öffnenden geschweiften Klammer vor 'class'
        start_bracket_index = text.rfind(
            "{", max(0, class_index - 20), class_index)

        if start_bracket_index == -1:
            continue

        # Finde die entsprechende schließende Klammer für die öffnende Klammer

        end_bracket_index = find_end_bracket(text, start_bracket_index)

        if not end_bracket_index:
            continue

        # Extrahiere den Teil des Textes zwischen den Klammern
        text = text[:start_bracket_index] + text[end_bracket_index + 1:]

    return text


def extract_infobox_parts(text):
    '''
    Sucht nach allen Infoboxen im String 'text' und entfernt diese
    Return: gefilterter Text
    '''

    indices = collect_indices(text.lower(), "infobox")

    # Iteriere rückwärts durch die Indize Liste, um bei jedem Löschen, die Position nicht neu berechnen zu müssen
    for infobox_index in indices[::-1]:

        # Suche nach den öffnenden geschweiften Klammern vor 'infobox'
        start_bracket_index = text.rfind(
            "{{", max(0, infobox_index - 10), infobox_index)

        if start_bracket_index == -1:
            continue

        # Finde die entsprechende schließende Klammer für die öffnende Klammer

        end_bracket_index = find_end_bracket(text, start_bracket_index)

        if not end_bracket_index:
            continue

        # Extrahiere den Teil des Textes zwischen den Klammern
        text = text[:start_bracket_index] + text[end_bracket_index + 1:]

    return text


def collect_indices(text, term):
    ''' 
    Gibt alle Startindizes des gesuchten Termes eines Strings zurück als Liste 
    '''
    matches = re.finditer(term, text)
    return [match.start() for match in matches]


def find_end_bracket(text, start_bracket_index):
    '''
    Sucht innerhalb eines Textes (String) anhand des Indexes einer öffnenden,
    geschwungenen Klammer nach der entsprechenden schließenden Klammer,
    auch bei Verschachtelungen

    Return: der Index des Textes der schließenden Klammer
    '''
    counter = 0
    current_index = start_bracket_index

    # Suche nach öffnenden oder schließenden Klammern
    bracket_match = re.search("{|}", text[current_index:])

    while bracket_match:

        if bracket_match.group() == "}":
            # Die letzte öffnende Klammer
            if counter == 1:
                # Keine offenen Klammern mehr
                return current_index + bracket_match.start()
            else:
                counter -= 1
        elif bracket_match.group() == "{":

            counter += 1
        current_index = current_index + bracket_match.start() + 1
        bracket_match = re.search("{|}", text[current_index:])


def remove_irrelevant_paragraphs(text):
    ''' 
    Löschen von Abschnitten bis zum Ende anhand bestimmter Überschriften
    Return: gefilterter/ gekürzter Text
    '''

    headings = ["See also", "External Links", "Notes", "Footnotes",
                "References", "Further Reading", "Bibliography", "Citations"]

    for heading in headings:
        pattern = re.compile(r'(={1,})\s*' + heading.lower() + '\s*(={1,})')
        matches = pattern.finditer(text.lower())
        for match in matches:
            text = text[:match.start()]

    return text
