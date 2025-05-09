import json
import unicodedata

def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

obce = read_json("./data/locations/obce.json")["polozky"]
okresy = read_json("./data/locations/okresy.json")["polozky"]
kraje = read_json("./data/locations/kraje.json")["polozky"]
casti_obci = read_json("./data/locations/casti-obci.json")["polozky"]
casti_mest = read_json("./data/locations/obvody-casti.json")["polozky"]

populace_obce_casti = read_json("./data/locations/populace.json")
populace_kraje_okresy = read_json("./data/locations/populace-regiony, okresy.json")["List1"]

location_map = {}
muni_with_parts = set()

regions = []
for item in kraje:
    id_ = "reg" + item["kod"]
    weight = next((a.get("Column3") for a in populace_kraje_okresy if a and a.get("Column2") == item["nazev"]["cs"]), None)
    region = {
        "id": id_,
        "kod": int(item["kod"]),
        "label": item["nazev"]["cs"],
        "detail": None,
        "weight": weight,
        "startIndexes": [0]
    }
    regions.append(region)
    location_map[id_] = {"type": "reg", "region": id_}

districts = []
for x in okresy:
    id_ = "dist" + x["kod"]
    region = next((a for a in regions if a["kod"] == int(x["kraj"].split("/")[1])), None)
    weight = next((a.get("Column3") for a in populace_kraje_okresy if a and a.get("Column2") == x["nazev"]["cs"]), None)
    district = {
        "id": id_,
        "kod": int(x["kod"]),
        "label": "Okres " + x["nazev"]["cs"],
        "detail": None,
        "region": region["label"],
        "regionID": region["id"],
        "weight": weight,
        "startIndexes": [0, 6]
    }
    districts.append(district)
    location_map[id_] = {"type": "dist", "region": region["id"]}

municipalities = []
for x in obce:
    id_ = "muni" + x["kod"]
    indexes = [0, x["nazev"]["cs"].index("-")+1] if "-" in x["nazev"]["cs"] else [0]
    district = next((a for a in districts if a["kod"] == int(x["okres"].split("/")[1])), None)
    region = next((a for a in regions if district and district["regionID"] == a["id"]), None)
    weight = next((a['hodnota'] for a in populace_obce_casti if int(a['uzemi_kod']) == int(x['kod']) and a['pohlavi_txt'] == "" and a['uzemi_txt'] == x['nazev']['cs']),   0)    
    detail = district["label"]
    municipality = {
        "id": id_,
        "kod": int(x["kod"]),
        "label": x["nazev"]["cs"],
        "detail": detail,
        "districtID": district["id"],
        "district": district["label"],
        "regionID": region["id"],
        "region": region["label"],
        "weight": weight,
        "startIndexes": indexes
    }
    municipalities.append(municipality)
    location_map[id_] = {
        "type": "muni",
        "region": region["id"],
        "district": district["id"],
    }

city_parts = []
for x in casti_mest:
    id_ = "citypart" + str(x["kod"])
    indexes = [0, x["nazev"]["cs"].index("-")+1] if "-" in x["nazev"]["cs"] else [0]
    municipality = next((a for a in municipalities if a["kod"] == int(x["obec"].split("/")[1])), None)
    district = next((a for a in districts if municipality and municipality["districtID"] == a["id"]), None)
    region = next((a for a in regions if district and district["regionID"] == a["id"]), None)
    weight = next((a['hodnota'] for a in populace_obce_casti if int(a['uzemi_kod']) == int(x['kod']) and a['pohlavi_txt'] == "" and a['uzemi_txt'] == x['nazev']['cs']),   0)    

    detail = municipality["label"]
    city_part = {
        "id": id_,
        "kod": int(x["kod"]),
        "label": x["nazev"]["cs"],
        "detail": detail,
        "municipalityID": municipality["id"],
        "municipality": municipality["label"],
        "districtID": district["id"],
        "district": district["label"],
        "regionID": region["id"],
        "region": region["label"],
        "weight": weight,
        "startIndexes": indexes
    }
    city_parts.append(city_part)
    location_map[id_] = {
        "type": "citypart",
        "region": region["id"],
        "district": district["id"], 
        "municipality": municipality["id"],
    }
    if municipality:
        muni_with_parts.add(municipality["id"])

muni_parts = []
for x in casti_obci:
    id_ = "munipart" + x["kod"]
    indexes = [0, x["nazev"]["cs"].index("-")+1] if "-" in x["nazev"]["cs"] else [0]
    municipality = next((a for a in municipalities if a["kod"] == int(x["obec"].split("/")[1])), None)
    district = next((a for a in districts if municipality and municipality["districtID"] == a["id"]), None)
    region = next((a for a in regions if district and district["regionID"] == a["id"]), None)
    detail = municipality["label"]
    if municipality and municipality["label"] != x["nazev"]["cs"]:
        weight = next((a['hodnota'] for a in populace_obce_casti if int(a['uzemi_kod']) == int(x['kod']) and a['pohlavi_txt'] == "" and a['uzemi_txt'] == x['nazev']['cs']),   0)    
        muni_part = {
            "id": id_,
            "kod": int(x["kod"]),
            "label": x["nazev"]["cs"],
            "detail": detail,
            "municipalityID": municipality["id"],
            "municipality": municipality["label"],
            "districtID": district["id"],
            "district": district["label"],
            "regionID": region["id"],
            "region": region["label"],
            "weight": weight,
            "startIndexes": indexes
        }
        muni_parts.append(muni_part)
        location_map[id_] = {
            "type": "munipart",
            "region": region["id"],
            "district": district["id"],
            "municipality": municipality["id"]
        }
        muni_with_parts.add(municipality["id"])

locations = regions + districts + municipalities + city_parts + muni_parts

def normalize_string(input_str):
    s = input_str.lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("-", " ")
    return s


def preprocess_locations(locations):
    return sorted([
        {
            "label": loc["label"],
            "normalized": normalize_string(loc["label"]),
            "detail": loc["detail"],
            "startIndexes": loc["startIndexes"],
            "id": loc["id"],
            "weight": loc["weight"]
        }
        for loc in locations
    ], key=lambda x: x["normalized"])

preprocessed_locations = preprocess_locations(locations)

write_json("./locations.json", preprocessed_locations)
write_json("./locationMap.json", list(location_map.items()))
write_json("./muniWithParts.json", list(muni_with_parts))