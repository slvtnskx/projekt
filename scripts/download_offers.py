import requests

URL = "https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json"
OUTPUT_FILE = "volna-mista.json"

def download_data():
    print(f"Downloading data from {URL}...")
    response = requests.get(URL)
    response.raise_for_status()
    with open(OUTPUT_FILE, "wb") as f:
        f.write(response.content)
    print(f"Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    download_data()
