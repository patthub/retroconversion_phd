import json
from pymarc import MARCReader
from tqdm import tqdm


from pymarc import MARCReader, MARCWriter

def divide_marc_file(marc_filename, parts=10):
    # Wczytywanie wszystkich rekordów
    with open(marc_filename, 'rb') as marc_file:
        reader = MARCReader(marc_file)
        records = [record for record in reader]

    # Obliczanie rozmiaru każdej części
    total_records = len(records)
    part_size = total_records // parts
    for part in tqdm(range(parts)):
        start = part * part_size
        end = start + part_size if part != parts - 1 else total_records

        # Zapisywanie części do nowego pliku
        part_filename = f"{marc_filename}_part_{part + 1}.marc"
        with open(part_filename, 'wb') as part_file:
            writer = MARCWriter(part_file)
            for record in tqdm(records[start:end]):
                writer.write(record)
            writer.close()

marc_filename = 'bibs-artykul.marc' 
# divide_marc_file(marc_filename)


def convert_marc_to_json(marc_filename, json_filename):
    # Otwieranie pliku MARC i odczytywanie rekordów
    with open(marc_filename, 'rb') as marc_file:
        reader = MARCReader(marc_file)
        records = []
        for record in tqdm(reader):
            # Konwersja rekordu MARC na słownik i dodanie do listy
            records.append(record.as_dict())

    # Zapisywanie rekordów do pliku JSON
    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(records, json_file, ensure_ascii=False, indent=4)

# Użycie funkcji
marc_filename = 'bibs-artykul.marc' 
json_filename = 'bibs-artykul.json'  
# convert_marc_to_json(marc_filename, json_filename)
