import pandas as pd
import numpy as np
import requests
import json
from tqdm import tqdm
from joblib import Parallel, delayed



field_mapping = {
  
    "person": "marc=100a+",
    "organization": "marc=110a+",
    "event": "marc=111a+",
    "place": "marc=151a+",
    "subject": "marc=150a+"
}


def query_data_bn_authorities(term, field):
  


    BASE_BN_URL = f"http://data.bn.org.pl/api/institutions/authorities.json?{field}"
    url = BASE_BN_URL + term
    responses = []
    while url:
        response = requests.get(url)
        if response.status_code == 200:
            response_json = response.json()
            responses.append(response_json)
            url = response_json.get("nextPage", None)
        else:
            print("Error while accessing API")
            break
    return responses

def query_omnis(term, query_endpoint):
    BASE_BN_URL = f"https://omnis.bn.org.pl/api/work/list?metadata%5B0%5D.label={query_endpoint}&metadata%5B0%5D.value={term}"
    url = BASE_BN_URL
    responses = []
    while url:
        response = requests.get(url)
        if response.status_code == 200:
            response_json = response.json()
            responses.append(response_json)
            url = None  # Zmiana, ponieważ brak paginacji w API
        else:
            print("Error while accessing API")
            break
    return responses

def get_record_id(record):
    for field in record[0][0]["bibs"][0]["marc"]["fields"]:
        for k, v in field.items():
            if k == "009":
                return v
    return None

def query_omnis_by_id(record):
    id = get_record_id(record)
    if id:
        BASE_BN_URL = f"https://omnis.bn.org.pl/api/work/list?metadata%5B0%5D.label=search_identity&metadata%5B0%5D.value={id}"
        response = requests.get(BASE_BN_URL.strip())
        if response.status_code == 200:
            return response.json()
        else:
            print("Error while accessing API")
    return None

def query_data_bn_authorities_joblib(terms, field):
    results = Parallel(n_jobs=-1)(delayed(query_data_bn_authorities)(term, field) for term in terms)
    return results

def query_omnis_by_id_joblib(records):
    results = Parallel(n_jobs=-1)(delayed(query_omnis_by_id)(record) for record in records)
    return results
