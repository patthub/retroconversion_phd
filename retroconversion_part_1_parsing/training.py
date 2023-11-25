import pandas as pd
import numpy as np

import spacy
from spacy import displacy
from spacy.tokens import DocBin
from spacy.util import minibatch, compounding

from langdetect import detect

import os
from tqdm import tqdm
import regex as re
import random
from pathlib import Path
from tqdm import tqdm
import json


from enums import *


#FUNCTIONS FOR PREPARING DATA

def readFile(path):
    main_file = pd.DataFrame(open(path, "r").readlines(), columns=['Record'])
    return main_file

def prepare_df(path: str, delimiters: list) -> pd.DataFrame:
    

    df = readFile(path).rename(columns={'Nazwa': 'Records'})
    df["Record"].replace('', np.nan, inplace=True)
    df.dropna(subset=["Record"], inplace=True)
    df['digit'] = df["Record"].str.contains("^\\d{1,4}\\.", regex=True)
    df['row_id'] = np.arange(len(df))

    def f(row):
        if row['digit'] == True:
            val = row['row_id']
            return val
    df['id'] = df.apply(lambda x: f(x), axis = 1)
    df
    df['id'].ffill(axis=0, inplace=True)
    df = df.groupby('id')['Record'].apply(' '.join).reset_index()
    df['Record']

    dane_dict = df["Record"].to_dict()
    lista = []
    for delimiter in delimiters:
        for v in dane_dict.values():
            lista.append(pd.DataFrame(re.split(delimiter, v)))
    new_df = pd.concat(lista).rename(columns={0: 'Records'})
    new_df["PERSON"] = new_df["Records"].apply(find_person)
    new_df["PERSON_to_replace"] = ["".join(row) for row in new_df["PERSON"]]
    new_df["Records"] = [row1.replace(row2, "") for row1, row2 in zip(new_df['Records'],new_df["PERSON_to_replace"])]
    new_df["Records"] = [row.replace("\n", "") for row in new_df["Records"]]
    new_df.drop('PERSON_to_replace',axis='columns', inplace=True)
    
    def y(row):
        if len(row) == 0:
            row = None
        return row
      
    #new_df["PERSON"] = new_df["PERSON"].apply(lambda x: None if len(x) == 0 else x)
    new_df["PERSON"] = new_df["PERSON"].apply(y)
    new_df["PERSON"] = new_df["PERSON"].ffill(axis = 0)
    new_df['PERSON'] = new_df['PERSON'].shift(+1)
  
    return new_df


def find_person(row):
    person = re.findall(PATTERN_PERSON_SUBJECT, row)
    return person


def det(x):
    try:
        lang = detect(x)
    except:
        lang = 'Other'
    return lang


#FUNCTIONS FOR DATA PROCESSING
def prepare_training_data_regex(records, regex, label):
    TRAIN = []
    for record in records:
        for match in re.finditer(regex, record):
            start, end = match.span()
            record_train = (record, {"entities": [(start, end, label)]})
            TRAIN.append(record_train)
    return TRAIN


#FUNCTION FOR MODEL TRAINING
def train_model(TRAIN_DATA): 
    nlp=spacy.blank("pl")
    nlp.add_pipe('ner')
    nlp.begin_training()
    ner = nlp.get_pipe("ner")
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])
    from spacy.training.example import Example
    for iteration in range(100):
        random.shuffle(TRAIN_DATA)
        losses = {}
        batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
        for batch in tqdm(batches):
            #texts, annotations = zip(*batch)
            for text, annotations in batch:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                nlp.update(
                            [example],
                            drop=0.5, 
                            losses=losses,
                        )
    return nlp

def get_ents(row):
    entities = []
    doc = nlp(row)
    for ent in doc.ents:
        entities.append(f"{ent.text}, {ent.label_}")
    return entities



with open(r"C:\Users\patry\Desktop\Doktorat_code\annotations_20_01_1.json", "r", encoding = "utf8") as f:
  data = json.load(f)
  
  
data1 = []
for elem in data["annotations"]:
  data1.append(tuple(elem))

  
train = data1.copy()

db = DocBin() 
nlp = spacy.blank("pl")

for text, annot in tqdm(train):
    doc = nlp.make_doc(text) 
    ents = []
    for start, end, label in annot["entities"]: 
        span = doc.char_span(start, end, label=label, alignment_mode="contract")
        if span is None:
            print("Skipping entity")
        else:
            ents.append(span)
    doc.ents = ents 
    db.add(doc)

db.to_disk("./train.spacy") 
