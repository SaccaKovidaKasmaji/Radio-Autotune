import requests, re, time, logging
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from database import RadioStation, SessionLocal, init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

TARGETS = {
    "DKI Jakarta":   "https://id.wikipedia.org/wiki/Daftar_stasiun_radio_di_DKI_Jakarta",
    "Jawa Barat":    "https://id.wikipedia.org/wiki/Daftar_stasiun_radio_di_Jawa_Barat",
    "Jawa Tengah":   "https://id.wikipedia.org/wiki/Daftar_stasiun_radio_di_Jawa_Tengah",
    "Jawa Timur":    "https://id.wikipedia.org/wiki/Daftar_stasiun_radio_di_Jawa_Timur",
    "DI Yogyakarta": "https://id.wikipedia.org/wiki/Daftar_stasiun_radio_di_Daerah_Istimewa_Yogyakarta",
    "Banten":        "https://id.wikipedia.org/wiki/Daftar_stasiun_radio_di_Banten",
    "Bali":          "https://id.wikipedia.org/wiki/Daftar_stasiun_radio_di_Bali",
}
#Data manual tambahan dari scrapping
DATA_MANUAL = [
    # Kota Bandung
    {"nama_stasiun": "Ardan FM",           "frekuensi_mhz": 105.9, "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "OZ Radio",           "frekuensi_mhz": 103.1, "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "RRI Pro 1",          "frekuensi_mhz": 91.4,  "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "RRI Pro 2",          "frekuensi_mhz": 105.1, "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "RRI Pro 3",          "frekuensi_mhz": 95.3,  "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "RRI Pro 4",          "frekuensi_mhz": 97.6,  "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "Elshinta Bandung",   "frekuensi_mhz": 100.9, "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "Pass FM",            "frekuensi_mhz": 102.2, "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "Rama FM",            "frekuensi_mhz": 98.7,  "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "KLCBS FM",           "frekuensi_mhz": 100.4, "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "Dahlia FM",          "frekuensi_mhz": 101.5, "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "Motion Radio",       "frekuensi_mhz": 97.5,  "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "Cosmo FM",           "frekuensi_mhz": 101.9, "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "Female Radio",       "frekuensi_mhz": 99.5,  "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "Prambors Bandung",   "frekuensi_mhz": 98.4,  "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "I-Radio Bandung",    "frekuensi_mhz": 89.6,  "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "Hard Rock FM Bandung","frekuensi_mhz": 87.6, "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "Imelda FM",          "frekuensi_mhz": 88.5,  "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "Gapura FM",          "frekuensi_mhz": 107.7, "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "MQ FM",              "frekuensi_mhz": 102.7, "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "RKPD FM",            "frekuensi_mhz": 96.0,  "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "Fajri FM",           "frekuensi_mhz": 91.7,  "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "Mustang FM",         "frekuensi_mhz": 88.0,  "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "Trijaya FM Bandung", "frekuensi_mhz": 92.0,  "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "Pop FM Bandung",     "frekuensi_mhz": 90.5,  "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "SL FM",             "frekuensi_mhz": 93.6,  "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "Bens Radio Bandung", "frekuensi_mhz": 106.2, "kota": "Kota Bandung", "provinsi": "Jawa Barat"},
    {"nama_stasiun": "Sonata FM",          "frekuensi_mhz": 94.3,  "kota": "Kota Bandung", "provinsi": "Jawa Barat"},

    # DKI Jakarta
    {"nama_stasiun": "Prambors FM",    "frekuensi_mhz": 102.2, "kota": "Jakarta Selatan", "provinsi": "DKI Jakarta"},
    {"nama_stasiun": "Hard Rock FM",   "frekuensi_mhz": 87.6,  "kota": "Jakarta Selatan", "provinsi": "DKI Jakarta"},
    {"nama_stasiun": "CBS FM",         "frekuensi_mhz": 95.9,  "kota": "Jakarta Selatan", "provinsi": "DKI Jakarta"},
    {"nama_stasiun": "Elshinta",       "frekuensi_mhz": 90.0,  "kota": "Jakarta Barat",   "provinsi": "DKI Jakarta"},
    {"nama_stasiun": "Gen FM",         "frekuensi_mhz": 98.7,  "kota": "Jakarta Selatan", "provinsi": "DKI Jakarta"},
    {"nama_stasiun": "Trijaya FM",     "frekuensi_mhz": 104.6, "kota": "Jakarta Pusat",   "provinsi": "DKI Jakarta"},
    {"nama_stasiun": "Delta FM",       "frekuensi_mhz": 99.1,  "kota": "Jakarta Selatan", "provinsi": "DKI Jakarta"},
    {"nama_stasiun": "Motion FM",      "frekuensi_mhz": 97.5,  "kota": "Jakarta Selatan", "provinsi": "DKI Jakarta"},
    {"nama_stasiun": "I-Radio Jakarta","frekuensi_mhz": 89.6,  "kota": "Jakarta Pusat",   "provinsi": "DKI Jakarta"},
    {"nama_stasiun": "RRI Pro 3 Jakarta","frekuensi_mhz": 91.2,"kota": "Jakarta Pusat",   "provinsi": "DKI Jakarta"},

    # DI Yogyakarta
    {"nama_stasiun": "Geronimo FM",    "frekuensi_mhz": 106.1, "kota": "Kota Yogyakarta", "provinsi": "DI Yogyakarta"},
    {"nama_stasiun": "Prambors Yogya", "frekuensi_mhz": 95.8,  "kota": "Kota Yogyakarta", "provinsi": "DI Yogyakarta"},
    {"nama_stasiun": "RRI Pro 2 Yogya","frekuensi_mhz": 91.1,  "kota": "Kota Yogyakarta", "provinsi": "DI Yogyakarta"},

    # Jawa Timur
    {"nama_stasiun": "Paramuda FM",    "frekuensi_mhz": 100.2, "kota": "Kota Surabaya",   "provinsi": "Jawa Timur"},
    {"nama_stasiun": "Prambors Surabaya","frekuensi_mhz": 89.3,"kota": "Kota Surabaya",   "provinsi": "Jawa Timur"},
    {"nama_stasiun": "Hard Rock Surabaya","frekuensi_mhz": 91.3,"kota": "Kota Surabaya",  "provinsi": "Jawa Timur"},
]

def bersihkan_frekuensi(teks):
    if not teks: return None
    dibersihkan = re.sub(r"[^\d.,]", "", teks.strip()).replace(",", ".")
    bagian = dibersihkan.split(".")
    if len(bagian) > 2:
        dibersihkan = bagian[0] + "." + bagian[1]
    try:
        f = float(dibersihkan)
        return f if 87.5 <= f <= 108.0 else None
    except ValueError:
        return None

def bersihkan_teks(teks):
    return " ".join(teks.strip().split()) if teks else ""

def simpan(data_list, db):
    jumlah = 0
    for data in data_list:
        ada = db.query(RadioStation).filter(
            RadioStation.nama_stasiun  == data["nama_stasiun"],
            RadioStation.frekuensi_mhz == data["frekuensi_mhz"]
        ).first()
        if not ada:
            db.add(RadioStation(**data))
            jumlah += 1
    db.commit()
    return jumlah

def scrape_provinsi(provinsi, url):
    hasil = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "lxml")
        for tabel in soup.find_all("table", class_="wikitable"):
            baris_list = tabel.find_all("tr")
            if len(baris_list) < 2: continue
            headers = [bersihkan_teks(h.get_text()).lower()
                       for h in baris_list[0].find_all(["th", "td"])]
            idx_nama = next((i for i, h in enumerate(headers)
                             if any(k in h for k in ["nama", "stasiun", "radio"])), None)
            idx_frek = next((i for i, h in enumerate(headers)
                             if any(k in h for k in ["frekuensi", "freq", "mhz"])), None)
            idx_kota = next((i for i, h in enumerate(headers)
                             if any(k in h for k in ["kota", "kabupaten", "wilayah", "lokasi"])), None)
            if idx_nama is None or idx_frek is None: continue
            for baris in baris_list[1:]:
                cells = baris.find_all(["td", "th"])
                if len(cells) <= max(filter(None, [idx_nama, idx_frek])): continue
                nama = bersihkan_teks(cells[idx_nama].get_text())
                frek = bersihkan_frekuensi(cells[idx_frek].get_text())
                kota = bersihkan_teks(cells[idx_kota].get_text()) if idx_kota and idx_kota < len(cells) else "Tidak diketahui"
                if nama and frek:
                    hasil.append({"nama_stasiun": nama, "frekuensi_mhz": frek,
                                  "kota": kota, "provinsi": provinsi})
    except Exception as e:
        logger.error(f"Gagal scrape {provinsi}: {e}")
    return hasil

def jalankan_scraping():
    logger.info("Mulai scraping...")
    init_db()
    db = SessionLocal()
    total = 0
    try:
        total += simpan(DATA_MANUAL, db)
        logger.info(f"Seed manual: +{total}")
        for provinsi, url in TARGETS.items():
            data = scrape_provinsi(provinsi, url)
            n = simpan(data, db)
            total += n
            logger.info(f"{provinsi}: +{n} stasiun")
            time.sleep(2)
    finally:
        db.close()
    logger.info(f"Selesai. Total baru: {total}")

if __name__ == "__main__":
    jalankan_scraping()
