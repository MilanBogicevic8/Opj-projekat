import requests
from bs4 import BeautifulSoup
import os
import shutil

URL = "https://www.paragraf.rs/propisi/clanovi/"
LINKS_FILE = "administrative_texts_links.txt"
METADATA_FILE = "metadata.txt"
OUTPUT_FOLDER = "../../data/administrative_documents"

def scrape_admin_links():

    if os.path.exists(LINKS_FILE):
        os.remove(LINKS_FILE)
        print(f"Obrisan stari fajl: {LINKS_FILE}")

    response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        print(f"Greška: {response.status_code}")
        return

    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    main_div = soup.find("div", id="main")

    if not main_div:
        print("Div sa id='main' nije pronađen.")
        return

    links = []
    for a in main_div.find_all("a", href=True):
        href = a["href"]
        links.append(URL + href)

    links = list(set(links))

    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        for link in links:
            f.write(link + "\n")

    print(f"Snimljeno {len(links)} linkova u {LINKS_FILE}")

def scrape_administrative_docs():
    if os.path.exists(OUTPUT_FOLDER) and os.path.isdir(OUTPUT_FOLDER):
        shutil.rmtree(OUTPUT_FOLDER)
        print(f"Obrisan direktorijum: {OUTPUT_FOLDER}")

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    if os.path.exists(METADATA_FILE):
        os.remove(METADATA_FILE)

    with open(LINKS_FILE, "r", encoding="utf-8") as f:
        links = [line.strip() for line in f.readlines()]
    #dodavanje i ustava srbije kao primera administrativnog teksta
    links = ["https://www.paragraf.rs/propisi/ustav_republike_srbije.html"] + links
    total_tokens = 0

    for i, link in enumerate(links, start=1):
        try:
            response = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code != 200:
                print(f"Greška kod {link}: {response.status_code}")
                continue
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            text = "\n".join(p.get_text() for p in paragraphs if p.get_text().strip())

            if not text:
                continue

            filename = f"doc_{i}.txt"
            filepath = os.path.join(OUTPUT_FOLDER, filename)
            with open(filepath, "w", encoding="utf-8") as tf:
                tf.write(text)

            with open(METADATA_FILE, "a", encoding="utf-8") as mf:
                mf.write(f"{filename}\t{link}\n")

            total_tokens += len(text.split())

            print(f"Snimljeno: {filename}")

        except Exception as e:
            print(f"Greška kod {link}: {e}")

    print(f"Ukupan broj tokena: {total_tokens}")

if __name__ == "__main__":
    scrape_admin_links()
    scrape_administrative_docs()
