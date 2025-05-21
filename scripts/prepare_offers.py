import json
from pathlib import Path

# Load locationMap as a dict of dicts for fast lookup
with open("locationMap.json", encoding="utf-8") as f:
    location_map = dict(json.load(f))

def calculate_wage(item, target_type, source_field):
    if not item.get(source_field):
        return None
    typ_mzdy = item.get("typMzdy", {})
    current_type = typ_mzdy.get("id", "").split("/")[1] if typ_mzdy.get("id") else None
    if current_type == target_type:
        return round(item[source_field], 2)
    hours_per_week = item.get("pocetHodinTydne") or 40
    if not hours_per_week:
        return None
    monthly_hours = hours_per_week * 4
    if target_type == "hod":
        result = item[source_field] / monthly_hours
    else:
        result = item[source_field] * monthly_hours
    return round(result, 2)

def find_id(id_to_use, type_to_find):
    found = location_map.get(id_to_use)
    if not found:
        print(id_to_use, type_to_find)
        return None
    return found.get(type_to_find)

def get_location_ids(item):
    misto = item.get("mistoVykonuPrace")
    if not isinstance(misto, dict):
        misto = {}
    typ_mista_obj = misto.get("typMistaVykonuPrace")
    typ_mista = None
    if isinstance(typ_mista_obj, dict) and typ_mista_obj.get("id"):
        typ_mista = typ_mista_obj["id"].split("/")[1]
    pracoviste = misto.get("pracoviste", [{}])[0].get("adresa", {}) if misto.get("pracoviste") else {}
    if typ_mista == "adrprov" and pracoviste:
        region_id = pracoviste.get("kraj", {}).get("id", "").split("/")[1] if pracoviste.get("kraj") else None
        district_id = pracoviste.get("okres", {}).get("id", "").split("/")[1] if pracoviste.get("okres") else None
        municipality_id = pracoviste.get("obec", {}).get("id", "").split("/")[1] if pracoviste.get("obec") else None
        city_part_id = pracoviste.get("mestskyObvodMestskaCast", {}).get("id", "").split("/")[1] if pracoviste.get("mestskyObvodMestskaCast") else None
        muni_part_id = pracoviste.get("castObce", {}).get("id", "").split("/")[1] if pracoviste.get("castObce") else None
        region_id = f"reg{region_id}" if region_id else None
        district_id = f"dist{district_id}" if district_id else None
        municipality_id = f"muni{municipality_id}" if municipality_id else None
        city_part_id = f"cityPart{city_part_id}" if city_part_id else None
        muni_part_id = f"muniPart{muni_part_id}" if muni_part_id else None
        if not municipality_id and city_part_id:
            municipality_id = find_id(city_part_id, "municipality")
        if not district_id and municipality_id:
            district_id = find_id(municipality_id, "district")
        if not region_id and district_id:
            region_id = find_id(district_id, "region")
        return {
            "region": region_id,
            "district": district_id,
            "municipality": municipality_id,
            "cityPart": city_part_id
        }
    return {}

def format_address(adresa):
    if not isinstance(adresa, dict):
        return None
    parts = [
        adresa.get("ulice"),
        adresa.get("cisloPopisne"),
        adresa.get("cisloOrientacni"),
        adresa.get("obec"),
        adresa.get("psc"),
        adresa.get("stat")
    ]
    return ", ".join(str(p) for p in parts if p)

def get_contact(item):
    kontakt = item.get("prvniKontaktSeZamestnavatelem", {})
    komu = kontakt.get("komuSeHlasit", {})
    kde = kontakt.get("kdeSeHlasit", {})
    def contact_name():
        parts = [
            komu.get("titulPredJmenem"),
            komu.get("jmeno"),
            komu.get("prijmeni"),
            komu.get("titulZaJmenem")
        ]
        # Capitalize jmeno and prijmeni
        def cap(s):
            return " ".join(w.capitalize() for w in s.split()) if isinstance(s, str) else ""
        name_parts = []
        for i, part in enumerate(parts):
            if not part:
                continue
            if i in (1, 2):
                part = cap(part)
            name_parts.append(part + (" " if i < 3 else ""))
        return "".join(name_parts).strip() or None
    return {
        "contactName": contact_name(),
        "contactPosition": komu.get("poziceVeSpolecnosti"),
        "contactEmail": komu.get("email"),
        "contactNumber": komu.get("telefon"),
        "contactPlace": kde.get("mistoKontaktu"),
        "contactPlaceAddress": format_address(kde.get("adresa")),
        "contactPlaceEmail": kde.get("email"),
        "contactPlaceNumber": kde.get("telefon"),
        "workplaceEmail": (
            item.get("mistoVykonuPrace", {}).get("pracoviste", [{}])[0].get("email")
            if item.get("mistoVykonuPrace", {}).get("pracoviste") else None
        ),
        "workplaceNumber": (
            item.get("mistoVykonuPrace", {}).get("pracoviste", [{}])[0].get("telefon")
            if item.get("mistoVykonuPrace", {}).get("pracoviste") else None
        ),
        "labourOffice": item.get("kontaktniPracoviste", {}).get("id")
    }

class RestructuredOffer:
    def __init__(self, item):
        locations = get_location_ids(item)
        self.id = int(item["portalId"])
        self.lastModified = item["datumZmeny"]
        self.minWageHourly = calculate_wage(item, "hod", "mesicniMzdaOd")
        self.minWageMonthly = calculate_wage(item, "mesic", "mesicniMzdaOd")
        self.region = locations.get("region")
        self.district = locations.get("district")
        self.municipality = locations.get("municipality")
        self.cityPart = locations.get("cityPart")
        self.profession = item["profeseCzIsco"]["id"].split("/")[1] if item.get("profeseCzIsco") and item["profeseCzIsco"].get("id") else None
        
        upresnujici = item.get("upresnujiciInformace")
        upresnujici_cs = ""
        if isinstance(upresnujici, dict):
            upresnujici_cs = upresnujici.get("cs") or ""
        
        self.textToSearch = item["pozadovanaProfese"]["cs"] + "\n" + upresnujici_cs
        self.education = item.get("minPozadovaneVzdelani", {}).get("id", "/").split("/")[1] if item.get("minPozadovaneVzdelani") and item["minPozadovaneVzdelani"].get("id") else None
        self.shifts = item.get("smennost", {}).get("id", "/").split("/")[1] if item.get("smennost") and item["smennost"].get("id") else None
        self.hours = item.get("pocetHodinTydne")
        
        vztahy = item.get("pracovnePravniVztahy", {})
        vztahy_id = None
        if isinstance(vztahy, dict):
            vztahy_id = vztahy.get("id", "").split("/")[1] if vztahy.get("id") else None
        elif isinstance(vztahy, list) and vztahy:
            vztahy_id = vztahy[0].get("id", "").split("/")[1] if isinstance(vztahy[0], dict) and vztahy[0].get("id") else None
        
        self.fullTime = vztahy_id == "plny"
        self.partTime = vztahy_id == "zkraceny"
        self.freelanceWork = vztahy_id == "dpp"
        self.shortTermEmployment = vztahy_id == "dpc"
        self.civilService = vztahy_id == "sluzebni"
        self.agencyContract = item.get("souhlasAgenturyAgentura", False)
        self.agencyTemporaryStaffing = item.get("souhlasAgenturyUzivatel", False)
        self.asylumSeeker = item.get("azylant", False)
        self.nonEUnational = item.get("cizinecMimoEu", False)
        self.blueCard = item.get("modraKarta", False)
        self.employeeCard = item.get("zamestnaneckaKarta", False)
       
        upresnujici_informace = item.get("upresnujiciInformace") or {}
        misto_vykonu = item.get("mistoVykonuPrace") or {}
        pracoviste_list = misto_vykonu.get("pracoviste") or [{}]
        if not isinstance(pracoviste_list, list) or not pracoviste_list:
            pracoviste_list = [{}]
        pracoviste = pracoviste_list[0] if isinstance(pracoviste_list[0], dict) else {}

        self.displayInformation = {
            "archived": False,
            "keywords": [],
            "label": item["pozadovanaProfese"]["cs"],
            "description": upresnujici_informace.get("cs", None),
            "location": format_address(pracoviste.get("adresa")),
            "locationName": pracoviste.get("nazev"),
            "addressPlaceID": pracoviste.get("adresa", {}).get("kodAdresnihoMista") if isinstance(pracoviste.get("adresa"), dict) else None,
            "isco": item.get("profeseCzIsco", {}).get("id"),
            "iscoGroup": [],  # enums not available, leave empty
            "wageType": item.get("typMzdy", {}).get("id", "").split("/")[1] if item.get("typMzdy") else None,
            "minWage": item.get("mesicniMzdaOd"),
            "maxWage": item.get("mesicniMzdaDo"),
            "hours": item.get("pocetHodinTydne"),
            "education": item.get("minPozadovaneVzdelani", {}).get("id", "/").split("/")[1] if item.get("minPozadovaneVzdelani") and item["minPozadovaneVzdelani"].get("id") else None,
            "shifts": item.get("smennost", {}).get("id", "/").split("/")[1] if item.get("smennost") and item["smennost"].get("id") else None,
            "employmentType": [
                vztahy_id
            ] if vztahy_id else None,
            "benefits": [
                {
                    "description": v.get("popis"),
                    "type": v.get("id")
                } for v in (item.get("vyhodyVolnehoMista") or [])
            ] if item.get("vyhodyVolnehoMista") else None,
            "languages": [
                {
                    "lang": l.get("jazyk", {}).get("id"),
                    "level": l.get("urovenZnalosti", {}).get("id")
                } for l in (item.get("pozadovanaJazykovaZnalost") or [])
            ] if item.get("pozadovanaJazykovaZnalost") else None,
            "skills": [
                {
                    "description": s.get("popis"),
                    "type": s.get("dovednost", {}).get("id")
                } for s in (item.get("pozadovanaDovednost") or [])
            ] if item.get("pozadovanaDovednost") else None,
            "educationDetails": [
                e.get("id") for e in (item.get("pozadovaneVzdelani") or [])
            ] if item.get("pozadovaneVzdelani") else None,
            "professionDetails": [
                p.get("id") for p in (item.get("pozadovanePovolani") or [])
            ] if item.get("pozadovanePovolani") else None,
            "availablePositions": item.get("pocetMist"),
            "employmentEndDate": item.get("terminUkonceniPracovnihoPomeru"),
            "employmentStartDate": item.get("terminZahajeniPracovnihoPomeru"),
            "publicAdmin": item.get("statniSpravaSamosprava", False),
            "employer": item.get("zamestnavatel", {}).get("nazev"),
            "employerICO": item.get("zamestnavatel", {}).get("ico"),
            "url": item.get("urlAdresa"),
            "agencyContract": item.get("souhlasAgenturyAgentura", False),
            "agencyTemporaryStaffing": item.get("souhlasAgenturyUzivatel", False),
            "asylumSeeker": item.get("azylant", False),
            "nonEUnational": item.get("cizinecMimoEu", False),
            "blueCard": item.get("modraKarta", False),
            "employeeCard": item.get("zamestnaneckaKarta", False),
            "suitabilityDetails": item.get("vhodnostiPracovnihoMista", {}).get("id") if item.get("vhodnostiPracovnihoMista") else None,
            "contact": get_contact(item),
            "created": item.get("datumVlozeni"),
            "lastEdited": item.get("datumZmeny"),
            "govID": item.get("referencniCislo")
        }
    def to_dict(self):
        return self.__dict__

def restructure(data):
    return [RestructuredOffer(item).to_dict() for item in data]

def main():
    with open("../0temporary/volna-mista.json", encoding="utf-8") as f:
        data = json.load(f)["polozky"]
    print("loaded data")
    offers = restructure(data)
    with open("job_offers.jsonl", "w", encoding="utf-8") as f:
        for offer in offers:
            f.write(json.dumps(offer, ensure_ascii=False) + "\n")
    print("finished")

if __name__ == "__main__":
    main()


