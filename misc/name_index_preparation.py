import re

def split_line_into_records(line):
    # Wzór do wykrywania nazwisk i numerów, uwzględniający złożone nazwiska
    pattern = r'\b[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+(?:[- ][A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)* \d+(?:[-,] ?\d+)*'
    return re.findall(pattern, line)

def process_file(filename):
    result = {}
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            records = split_line_into_records(line)
            for record in records:
                # Rozdzielenie nazwiska i numerów
                parts = record.rsplit(' ', 1)
                name = parts[0]
                numbers = parts[1].replace(',', '').split()
                result.setdefault(name, []).extend(numbers)
    return result
