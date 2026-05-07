import os
import signal
import firebase_admin
from firebase_admin import credentials, firestore
import subprocess, logging, time

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

proses_rtl    = None
frekuensi_aktif = None

def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    return firestore.client()

def tune_rtl(frekuensi_mhz):
    global proses_rtl, frekuensi_aktif
    if frekuensi_mhz == frekuensi_aktif:
        return
    subprocess.run("taskkill /f /im rtl_fm.exe", shell=True, capture_output=True)
    subprocess.run("taskkill /f /im ffplay.exe", shell=True, capture_output=True)
    if proses_rtl:
        proses_rtl.wait()
    time.sleep(1)
    freq_hz = int(frekuensi_mhz * 1_000_000)
    logger.info(f"Tuning ke {frekuensi_mhz} MHz")
    cmd = f"rtl_fm -f {freq_hz} -M wbfm -s 200000 -r 44100 - | ffplay -f s16le -ar 44100 -nodisp -"
    proses_rtl = subprocess.Popen(cmd, shell=True)
    frekuensi_aktif = frekuensi_mhz

def on_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        data = doc.to_dict()
        freq = data.get("frekuensi_mhz")
        nama = data.get("nama_stasiun", "?")
        kota = data.get("kota", "?")
        if freq:
            logger.info(f"PUSH diterima! {nama} {freq} MHz ({kota})")
            tune_rtl(freq)

def main():
    logger.info("Konek ke Firebase...")
    db      = init_firebase()
    doc_ref = db.collection("settings").document("current_settings")
    watch   = doc_ref.on_snapshot(on_snapshot)
    logger.info("Listener aktif. Menunggu push dari website...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Dihentikan")
        watch.unsubscribe()
        if proses_rtl:
            proses_rtl.terminate()

if __name__ == "__main__":
    main()