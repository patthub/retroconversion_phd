import pandas as pd 
import numpy as np 
from tqdm import tqdm 
import regex as re 
import json 
import requests
import Levenshtein


def read_file(path):
	with open(path, "r", encoding = "utf-8") as f:
		data = f.readlines()
	return data


def extract_bibliographic_source(line: str) -> list:
    
    '''
    Function for extracting information about single bibliographic source from PBL. 
    Function creates a dictionary with abbreviation of a given 
    '''
    
    try:
        single_bibliographic_source = {}
        temp = re.split("-|—", line)
        temp_value = re.split("\.", temp[1])[0]
        temp_value = re.sub("za rok \d+", "",  temp_value)
        temp_value = re.sub("\d+", "",  temp_value).strip()
        single_bibliographic_source["Abbreviation"] = temp[0].strip()
        single_bibliographic_source["Name"] = temp_value.strip()
                                     
        return single_bibliographic_source
    except IndexError:
        pass

def extract_abbreviation(line: str) -> list: 
    
    try:
        single_abbreviation = {}
        temp = re.split("-", line)
        single_abbreviation[temp[0].strip()] = temp[1].strip()
        return single_abbreviation
    except IndexError:
        pass


def get_data(k: str, v: str) -> list:
    
    BASE_BN_URL = "http://data.bn.org.pl/api/institutions/bibs.json?marc=245a"

    response_main = {}
    url = f"http://data.bn.org.pl/api/institutions/bibs.json?marc=245a+{v}"
    
    responses = []
    try:
        while url:
            url = requests.get(url)
            if url.status_code == 200:
                url = url.json()
                responses.append(url)
                url = url["nextPage"]
                print(f"Downloading: {url}, {v}")
            else:
                print("Error while accessing API")
        print("Download complete")
        response = responses[0]
        print(url)
        if len(response["bibs"]) > 0:
            
            response = dict({(k , v) for k, v in response["bibs"][0].items() if k in["author", "title", "id", "genre"]})
            response_main[k] = (v, response) 
            return response_main
        else:
            print("0 records found")
    except IndexError:
        pass



def get_data_for_bibliographic_source(v = "No data") -> list:
    
    BASE_BN_URL = "http://data.bn.org.pl/api/institutions/bibs.json?marc=245a"

    response_main = {}
    if len(v) < 2 or v == None:

        v = "Error, data not found"
    url = f"http://data.bn.org.pl/api/institutions/bibs.json?marc=245a+{v}"
    
    responses = []
    try:
        while url:
            url = requests.get(url)
            if url.status_code == 200:
                url = url.json()
                responses.append(url)
                url = url["nextPage"]
                print(url)

            else:
                print("Error while accessing API")
        
        # response = responses[0]
        final_responses = []
        for response in responses:
          if len(response["bibs"]) > 0:
              final_responses.append(response)
              return final_responses
          else:
              print("0 records found")
    except IndexError:
        pass



    
def magic_add_to_dict(key, value, dest):
    if key in dest:
        dest[key].append(value)
    else:
        dest[key] = [value]

      

def create_bibliographic_source_record(pbl_record):
    
    try:
        temp = get_data_for_bibliographic_source(pbl_record.get("Name"))
        hits = [] 
        single_rec = {}
        if temp != None and temp != "*":
            for elem in temp:
                for x in elem["bibs"]:
                    for field in x["marc"]["fields"]:
                        if "245" in field:
                            original_title = field["245"]["subfields"][0].get("a")
                            original_title = ''.join(e.lower() for e in original_title if e.isalnum())
                            single_rec["title_for_comparison"] = original_title
                            single_rec["whole_rec"] = x["marc"]["fields"]
                            hits.append(single_rec)
                            single_rec = {}

            quality_hits = []

            title_from_pbl = ''.join(e.lower() for e in pbl_record.get("Name") if e.isalnum())
            for record in hits:
                record["Levenshtein"] = (Levenshtein.ratio(title_from_pbl, record["title_for_comparison"]),title_from_pbl, record["title_for_comparison"])


            for hit in hits:
                if hit.get("Levenshtein")[0] == 1.0:
                    quality_hits.append(hit)
                    break
                elif hit.get("Levenshtein")[0] > 0.9:
                    quality_hits.append(hit)

            if len(quality_hits) > 0:

                final_hit = quality_hits[0]

                final_hit_filtered = {}
                for field in final_hit.get("whole_rec"):
                    if "009" in field:
                        final_hit_filtered["bn_id"] = field.get("009")
                    elif "130" in field:
                        final_hit_filtered["bn_unified_title"] = field.get("130").get("subfields")[0].get("a")
                    elif "245" in field:
                        final_hit_filtered["bn_title"] = field.get("245").get("subfields")[0].get("a")
                    elif "380" in field:
                        magic_add_to_dict("bn_form_of_work", field.get("380").get("subfields")[0].get("a"), final_hit_filtered)
                    elif "650" in field:
                        magic_add_to_dict("bn_subjects", field.get("650").get("subfields")[0].get("a"), final_hit_filtered)
                    elif "655" in field:
                        magic_add_to_dict("bn_genre_form", field.get("655").get("subfields")[0].get("a"), final_hit_filtered)
                    elif "700" in field:
                        magic_add_to_dict("bn_secondary_author", (field.get("700").get("subfields")[0].get("a"), field.get("700").get("subfields")[-1].get("e")), final_hit_filtered)

                pbl_record["BN_INFO"] = final_hit_filtered
            if pbl_record == None:
                print("No record")
            else:
                return pbl_record
    except AttributeError:
        print("No record found")
    except TypeError:
        print("No data found")
