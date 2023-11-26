from rdflib import Graph, Literal, RDF, URIRef, Namespace, SKOS, RDFS
from rdflib.namespace import FOAF, XSD, DC
import urllib.parse
import json
import unidecode
from SPARQLWrapper import SPARQLWrapper, JSON
import spacy 


nlp = spacy.load(r"C:/Users/patry/Desktop/Retroconversion_PBL_full_code/retroconversion_phd-main/retroconversion_part_1_parsing/training/config/output/model-best")
# Deklaracja przestrzeni nazw
RETROPBL = Namespace('https://retropbl.ibl.waw.pl/')
RETROPBL_PERSONS = Namespace('https://retropbl.ibl.waw.pl/authorities/persons/')
RETROPBL_PLACES = Namespace('https://retropbl.ibl.waw.pl/authorities/places/')
RETROPBL_SUBJECTS = Namespace('https://retropbl.ibl.waw.pl/authorities/subjects/')
SCHEMA = Namespace('http://schema.org/')

def create_graph(record):
    graph = Graph()
    graph.bind("schema", SCHEMA)

    # Budowa grafu
    graph.add((URIRef(RETROPBL + record["id"]), RDF.type, SCHEMA.Book))
    graph.add((URIRef(RETROPBL + record["id"]), SCHEMA.name, Literal(record["title"], lang='pl')))
    graph.add((URIRef(RETROPBL + record["id"]), SCHEMA.author, URIRef(RETROPBL_PERSONS + record["author_id"])))
    graph.add((URIRef(RETROPBL + record["id"]), SCHEMA.locationCreated, URIRef(RETROPBL_PLACES + record["placeOfPublication_id"])))
    graph.add((URIRef(RETROPBL + record["id"]), SCHEMA.about, URIRef(RETROPBL_SUBJECTS + record["subject_id"])))
    graph.add((URIRef(RETROPBL + record["id"]), SCHEMA.datePublished, Literal(record["yearOfPublication"])))

    return graph

# # Rekord do przetworzenia
# record = {
#     "id": "b1972000002050001",
#     "title": "Oświeceni i sentymentalni. Studia nad literaturą i życiem w Polsce w okresie trzech rozbiorów.",
#     "author_id": "a1962000100000128",
#     "placeOfPublication_id": "a1948000300000011",
#     "yearOfPublication": "1971",
#     "subject_id": "a1955000400000028",
# }

# # Tworzenie grafu
# graph = create_graph(record)

# # Serializacja grafu do formatu Turtle
# graph.serialize("graph.ttl", format="turtle")

import spacy

def ner_process(sentence):
    # Załadowanie modelu
    nlp = spacy.load(r"C:/Users/patry/Desktop/Retroconversion_PBL_full_code/retroconversion_phd-main/retroconversion_part_1_parsing/training/config/output/model-best")
    
    # Przetwarzanie zdania
    doc = nlp(sentence)
    
    # Budowanie listy encji
    entities = [{'entity': ent.text, 'label': ent.label_} for ent in doc.ents]

    # Tworzenie zdania oczyszczonego (tylko tytuły)
    clean_sentence = ' '.join(ent.text for ent in doc.ents if ent.label_ == 'TYTUŁ')

    # Zwracanie wyników wraz z oryginalnym i oczyszczonym zdaniem
    return {
        'original_sentence': sentence,
        'clean_sentence': clean_sentence,
        'entities': entities
    }


# def ner_process(sentence):
#     # Załadowanie modelu
#     nlp = spacy.load(r"C:/Users/patry/Desktop/Retroconversion_PBL_full_code/retroconversion_phd-main/retroconversion_part_1_parsing/training/config/output/model-best")

#     # Przetwarzanie zdania
#     doc = nlp(sentence)
    
#     # Budowanie słownika z wynikami NER
#     entities = [{'entity': ent.text, 'label': ent.label_} for ent in doc.ents]
    
#     return entities

zdanie = "Kleiner J.: Zarys dziejów literatury polskiej. Wyd. 2. T. 2: 1831-1918. Przejrz. i uzup. S.	Kawyn. Wrocł. 60 Ossol., s. 255, il., portr., tabele Rec.: Sawicki S. Tgp60 47:4."
doc1 = ner_process(zdanie)
print(doc1)

# for ent in doc1.ents:
#   print(ent.text, ent.label_)
