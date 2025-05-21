import unicodedata
import json
import os
from functools import lru_cache
import bisect

def normalize_string(input):
    text = input.lower()
    text = unicodedata.normalize('NFD', text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.replace('-', ' ')
    return text

diacritic_map = {
    'a': ['a', 'á'], 'c': ['c', 'č'], 'd': ['d', 'ď'], 'e': ['e', 'é', 'ě'], 'i': ['i', 'í'],
    'n': ['n', 'ň'], 'o': ['o', 'ó'], 'r': ['r', 'ř'], 's': ['s', 'š'], 't': ['t', 'ť'],
    'u': ['u', 'ú', 'ů'], 'ů': ['ů', 'ú'], 'ú': ['ů', 'ú'], 'y': ['y', 'ý'], 'z': ['z', 'ž'], " ": [' ', '-'],
}

def matches_query(query, label):
    lower_query = query.lower()
    lower_label = label.lower()
    for i, q_char in enumerate(lower_query):
        if i >= len(lower_label):
            return False
        l_char = lower_label[i]
        if q_char == ' ':
            if l_char != ' ' and l_char != '-':
                return False
        elif q_char == '-':
            if l_char != '-':
                return False
        elif q_char in diacritic_map:
            if l_char not in diacritic_map[q_char]:
                return False
        else:
            if q_char != l_char:
                return False
    return True

# may want to load this differently
@lru_cache(maxsize=1)
def load_locations():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'data', 'locations.json')
    with open(json_path, encoding='utf-8') as f:
        return json.load(f)

def binary_search(locations, query):
    normalized_query = normalize_string(query)
    keys = [loc['normalized'][:len(normalized_query)] for loc in locations]
    return bisect.bisect_left(keys, normalized_query)

def search_locations(query, locations):
    start_index = binary_search(locations, query)
    results = []
    normalized_query = normalize_string(query)
    for i in range(start_index, len(locations)):
        location = locations[i]
        if not location['normalized'].startswith(normalized_query):
            break
        if matches_query(query, location['label']):
            results.append(location)
    return sorted(results, key=lambda x: -(x.get('weight') or 0))
