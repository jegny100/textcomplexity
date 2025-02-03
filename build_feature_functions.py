# -*- coding: utf-8 -*-
import re
import os
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import spacy
import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize

'''
Sammlung an unterstützenden Funktionen zur Erstellung der Features

'''

porter_stemmer = PorterStemmer()
stem = porter_stemmer.stem


def text_to_words(text):
    # Splitten des Snippets in seine Wortstämme
    text = re.sub('[^A-Za-z]', ' ', text).lower()
    words = word_tokenize(text)
    words = [stem(word) for word in words]
    return words


def build_cefr_list():
    # CEFR Feature: Einlesen der Vokabeln
    cefr_list = pd.read_csv('feature_data/CEFR/vocab_list.csv')
    a1_set = set(cefr_list.loc[cefr_list['CEFR'] ==
                 'a1', 'Vocab'].str.lower().values)
    a2_set = set(cefr_list.loc[cefr_list['CEFR'] ==
                 'a2', 'Vocab'].str.lower().values)
    b1_set = set(cefr_list.loc[cefr_list['CEFR'] ==
                 'b1', 'Vocab'].str.lower().values)
    b2_set = set(cefr_list.loc[cefr_list['CEFR'] ==
                 'b2', 'Vocab'].str.lower().values)
    c1_set = set(cefr_list.loc[cefr_list['CEFR'] ==
                 'c1', 'Vocab'].str.lower().values)
    return a1_set, a2_set, b1_set, b2_set, c1_set


# CEFR Feature: Einlesen der Vokabeln
a1_set, a2_set, b1_set, b2_set, c1_set = build_cefr_list()

# NER Feature: Einlesen des Models
nlp = spacy.load("en_core_web_sm")


### CEFR VOKABELN ###
def cefr_vocab_calc(snippet):
    # Berechnen der prozentualen Verteilung der CEFR Kategorien für einen Snippet
    a1 = a2 = b1 = b2 = c1 = unknown = 0
    for word in word_tokenize(snippet.lower()):
        if word in a1_set:
            a1 += 1
        elif word in a2_set:
            a2 += 1
        elif word in b1_set:
            b1 += 1
        elif word in b2_set:
            b2 += 1
        elif word in c1_set:
            c1 += 1
        else:
            unknown += 1
    a1, a2, b1, b2, c1, unknown = np.array(
        [a1, a2, b1, b2, c1, unknown])/np.sum([a1, a2, b1, b2, c1, unknown])
    return a1, a2, b1, b2, c1, unknown

### NER ###
# Named Entity Recognition


def ner_calc(snippet):
    doc = nlp(snippet)
    pos_liste = '|'.join([token.tag_ for token in doc])
    dep_liste = '|'.join([token.dep_ for token in doc])
    pos_anteil = pd.Series(
        [pos_liste, dep_liste, len(doc.ents) / len(pos_liste)], index=['POS', 'DEP', 'NER'])

    return pos_anteil

### SATZLÄNGE ###


def max_sent_len(snippet):
    # Speichern der absoluten Länge des längsten Satzes
    sentence_list = sent_tokenize(snippet)
    return max([len(word_tokenize(sentence)) for sentence in sentence_list] + [0])


### WORD FREQUENCIES ###
word_frequencies = pd.read_csv('feature_data/Word_Frequencies.csv')
word_frequencies = word_frequencies.set_index('Word')
word_frequencies = word_frequencies['Frequency'].to_dict()


def geo_mean_prob(snippet):
    words = np.unique(text_to_words(snippet))
    return np.exp(np.log([word_frequencies.get(word, 1)
                          for word in words]).sum() / len(words))
