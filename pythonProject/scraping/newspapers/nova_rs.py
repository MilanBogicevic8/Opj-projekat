import requests
from bs4 import BeautifulSoup
import os
import re
import shutil

URL = "https://nova.rs/vesti/"
OUTPUT_FILE = "nova_news_links.txt"
METADATA_FILE = "metadata.txt"
TEXT_FOLDER = "../../data/newspapers"

def scrape_links():
    # Ako fajl postoji -> brisanje
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
        print(f"Obrisan stari fajl: {OUTPUT_FILE}")

    # Slanje GET zahtev
    response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        print(f"Greška: {response.status_code}")
        return

    # Parsiranje HTML-a
    soup = BeautifulSoup(response.text, "html.parser")

    # Dohvatanje linkova vesti
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("https://nova.rs/vesti/"):
            links.append(href)

    # Uklanjanje duplikata
    links = list(set(links))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for link in links:
            f.write(link + "\n")

    print(f"Snimljeno {len(links)} linkova u {OUTPUT_FILE}")

def scrape_articles():
    approx_num_of_tokens = 0
    if os.path.exists(TEXT_FOLDER) and os.path.isdir(TEXT_FOLDER):
        shutil.rmtree(TEXT_FOLDER)
        print(f"Obrisan direktorijum: {TEXT_FOLDER}")

    # Kreiranje foldera za tekstove ako ne postoji
    if not os.path.exists(TEXT_FOLDER):
        os.makedirs(TEXT_FOLDER)

    # Ako postoji metadata fajl -> brisanje
    if os.path.exists(METADATA_FILE):
        os.remove(METADATA_FILE)

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        links = [line.strip() for line in f.readlines()]

    for i, link in enumerate(links, start=1):
        try:
            response = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code != 200:
                print(f"Greška kod {link}: {response.status_code}")
                continue
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            txt = []
            for p in paragraphs:
                clean_text = p.get_text().strip().replace("\n", " ")
                clean_text = re.sub(r'\s+', ' ', clean_text)
                if len(clean_text) > 5:
                    txt.append(clean_text)
            text = "\n".join(txt)
            approx_num_of_tokens += len(text.split(" "))

            if not text or  len(text) < 100:
                continue  # ako nema teksta ili je tekst kraci od 100 karaktera ide se na naredno citanje

            filename = f"article_{i}.txt"
            filepath = os.path.join(TEXT_FOLDER, filename)
            with open(filepath, "w", encoding="utf-8") as tf:
                tf.write(text)

            # Upis metadata
            with open(METADATA_FILE, "a", encoding="utf-8") as mf:
                mf.write(f"{filename}\t{link}\n")

            print(f"Snimljeno: {filename}")

        except Exception as e:
            print(f"Greška kod {link}: {e}")
    print(f"Broj tokena u newspaperima je oko: {approx_num_of_tokens}")

if __name__ == "__main__":
    scrape_links()
    scrape_articles()